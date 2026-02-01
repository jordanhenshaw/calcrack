# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
import mathutils

from .ui import MIC_TYPE

SPEED_OF_SOUND_IN_MPS = 343
FPS_TO_MPS = 0.3048  # feet/sec -> meters/sec
INVALID_MIC_ERROR_SECONDS = 1.0   # penalty error used when prediction invalid
CONFIDENCE_TO_WEIGHT = {1: 1.0, 2: 2.0, 3: 3.0}

SCORE_TOLERANCE_SECONDS = 0.10  # T: 100 ms avg error => score 0
MIN_MICS_REQUIRED = 1          # optionally set to 3 if you want minimum coverage


class Algorithm:
    '''
    Context: We need to find out where a bullet was fired from. All we have is a bunch of non-time-synced audio recordings of a crack and thump.

    Problem: We need to test candidate shooting position/angle/speed solutions. We need to see if a possible solution would actually create the
    crack-thump delta-t times for each microphone, the ones we actually observe in the recordings.

    Solution: We must mathematically calculate the mach cone, see where it intersects each microphone, and calcluate the delay between that time
    and when the thump, or the bang from the rifle itself, would arrive. We must then avergae the accuracy scores for each microphone and determine
    the total accuracy score between all mics to deliver the final score for the candidate position/angle/speed.

    Final Output: Just a float on a 0-100% score like on a test.
    '''
    def __init__(self, context, ao):
        self.context = context
        self.rifle = ao

        # Scene units are in meters, delta t is in seconds, and confidence is on a 1-3 scale where 3 is high confidence.
        self.round_velocity = self.rifle.ammo_speed  # In FPS. feet per second

        # Cache mic observation data at time of firing (hypothesis snapshot)
        self.mic_data = self.get_all_mic_data()

        # Cache rifle geometry at time of firing (use world space)
        self.rifle_origin_world = self.rifle.matrix_world.translation.copy()
        self.rifle_direction_unit = self.get_rifle_direction(self.rifle)

        # Convert to meters/sec for the physics model
        self.bullet_speed_mps = float(self.round_velocity) * FPS_TO_MPS

        # Keep endpoint only for debug/visual sanity (not used as a physical limit)
        self.rifle_endpoint = self.get_rifle_endpoint(self.rifle)

        print(f"Velocity (FPS): {self.round_velocity}")
        print(f"Velocity (m/s): {self.bullet_speed_mps:.3f}")
        print(f"Mic Data: {self.mic_data}")
        print(f"Rifle origin (world): {self.rifle_origin_world}")
        print(f"Rifle direction (unit): {self.rifle_direction_unit}")
        print(f"Rifle endpoint (display): {self.rifle_endpoint}")

    def get_all_mic_data(self):
        all_mics = [
            empty for empty in bpy.context.scene.objects
            if empty.type == 'EMPTY' and empty.empty_display_type == MIC_TYPE
        ]

        mic_data = {}
        for mic in all_mics:
            mic_data[mic.name] = (mic.location.copy(), round(mic.delta_t, 3), mic.confidence)
        return mic_data

    def get_rifle_endpoint(self, obj):
        origin = obj.matrix_world.translation
        direction = self.get_rifle_direction(obj)
        return origin + direction * obj.empty_display_size

    def get_rifle_direction(self, obj):
        direction = obj.matrix_world.to_3x3() @ mathutils.Vector((0, 1, 0))
        return direction.normalized()


    def execute(self):
        predictions = self.predict_mic_delta_ts()
        error = self.compare(predictions)
        print(predictions)
        return self.calculate_score(error)
    
    def predict_mic_delta_ts(self):
        """
        Predict crack–thump delta-t for each microphone given the cached
        rifle origin/direction and bullet speed.

        Returns:
            dict: { mic_name: {predicted_delta_t, valid, reason, debug} }
        """
        predictions = {}

        rifle_origin_world = self.rifle_origin_world
        bullet_direction_unit = self.rifle_direction_unit

        bullet_speed_mps = self.bullet_speed_mps
        speed_of_sound_mps = float(SPEED_OF_SOUND_IN_MPS)

        # Mach cone geometry constant:
        # tan(theta) where sin(theta)=c/v  -> tan(theta)= c / sqrt(v^2 - c^2)
        sqrt_term = (bullet_speed_mps * bullet_speed_mps - speed_of_sound_mps * speed_of_sound_mps) ** 0.5
        mach_cone_tangent = speed_of_sound_mps / sqrt_term

        for mic_name, (mic_position, observed_delta_t, confidence) in self.mic_data.items():
            mic_position_world = mic_position.copy()
            vector_rifle_to_mic = mic_position_world - rifle_origin_world

            # Decompose mic position relative to bullet axis
            distance_along_trajectory = vector_rifle_to_mic.dot(bullet_direction_unit)
            perpendicular_vector = vector_rifle_to_mic - (distance_along_trajectory * bullet_direction_unit)
            perpendicular_distance_to_trajectory = perpendicular_vector.length

            # Thump (muzzle blast) arrival time
            thump_arrival_time = vector_rifle_to_mic.length / speed_of_sound_mps

            # Crack arrival time (steady-state Mach cone model)
            crack_arrival_time = (
                distance_along_trajectory +
                (perpendicular_distance_to_trajectory / mach_cone_tangent)
            ) / bullet_speed_mps

            valid = True
            reason = "ok"

            if crack_arrival_time < 0.0:
                valid = False
                reason = "negative_crack_time"

            predicted_delta_t = (thump_arrival_time - crack_arrival_time) if valid else None

            predictions[mic_name] = {
                "predicted_delta_t": predicted_delta_t,
                "valid": valid,
                "reason": reason,
                "debug": {
                    "mic_position": tuple(mic_position_world),
                    "rifle_origin": tuple(rifle_origin_world),
                    "bullet_direction": tuple(bullet_direction_unit),
                    "distance_along_trajectory_m": float(distance_along_trajectory),
                    "perpendicular_distance_m": float(perpendicular_distance_to_trajectory),
                    "crack_time_s": float(crack_arrival_time),
                    "thump_time_s": float(thump_arrival_time),
                    "observed_delta_t_s": float(observed_delta_t),
                    "confidence": int(confidence),
                    "bullet_speed_mps": float(bullet_speed_mps),
                    "speed_of_sound_mps": float(speed_of_sound_mps),
                }
            }

        return predictions

    def compare(self, predictions):
        """
        Compare predicted delta-t values against observed delta-t values.

        Args:
            predictions (dict): output of predict_mic_delta_ts()

        Returns:
            dict with per-mic error records plus summary fields:
            {
            "per_mic": { mic_name: {...} },
            "summary": {...}
            }
        """
        comparison = {"per_mic": {}, "summary": {}}

        total_weight = 0.0
        total_weighted_absolute_error = 0.0
        valid_mic_count = 0
        invalid_mic_count = 0

        for mic_name, prediction_record in predictions.items():
            predicted_delta_t = prediction_record.get("predicted_delta_t")
            is_valid = bool(prediction_record.get("valid", False))
            invalid_reason = prediction_record.get("reason", "unknown")

            # Pull observed data from the snapshot captured in __init__
            mic_position, observed_delta_t, confidence = self.mic_data[mic_name]

            # Map confidence to a numeric weight (simple linear weighting)
            weight = float(CONFIDENCE_TO_WEIGHT.get(int(confidence), 1.0))

            if not is_valid or predicted_delta_t is None:
                invalid_mic_count += 1

                # For invalid predictions we store a penalty error value.
                # The scoring stage can decide how harshly to treat this.
                absolute_error_seconds = float(INVALID_MIC_ERROR_SECONDS)

                comparison["per_mic"][mic_name] = {
                    "valid": False,
                    "reason": invalid_reason,
                    "observed_delta_t_s": float(observed_delta_t),
                    "predicted_delta_t_s": None,
                    "absolute_error_s": absolute_error_seconds,
                    "signed_error_s": None,
                    "confidence": int(confidence),
                    "weight": weight,
                    "debug": prediction_record.get("debug", {}),
                }

            else:
                valid_mic_count += 1

                # NOTE:
                # If your observed delta_t is actually (thump - crack) instead of (crack - thump),
                # then change this to: signed_error_seconds = (-(predicted_delta_t) - observed_delta_t)
                signed_error_seconds = float(predicted_delta_t) - float(observed_delta_t)
                absolute_error_seconds = abs(signed_error_seconds)

                comparison["per_mic"][mic_name] = {
                    "valid": True,
                    "reason": "ok",
                    "observed_delta_t_s": float(observed_delta_t),
                    "predicted_delta_t_s": float(predicted_delta_t),
                    "absolute_error_s": float(absolute_error_seconds),
                    "signed_error_s": float(signed_error_seconds),
                    "confidence": int(confidence),
                    "weight": weight,
                    "debug": prediction_record.get("debug", {}),
                }

            total_weight += weight
            total_weighted_absolute_error += weight * absolute_error_seconds

        mean_absolute_error = (total_weighted_absolute_error / total_weight) if total_weight > 0.0 else float("inf")

        comparison["summary"] = {
            "valid_mic_count": valid_mic_count,
            "invalid_mic_count": invalid_mic_count,
            "total_mic_count": len(predictions),
            "total_weight": total_weight,
            "weighted_mean_absolute_error_s": float(mean_absolute_error),
        }

        return comparison
    

    def calculate_score(self, comparison):
        """
        Option 1 (low-bias): confidence-weighted MAE mapped linearly to 0–100.

        wMAE = sum(weight_i * abs_error_i) / sum(weight_i)
        score = clamp(100 * (1 - wMAE / T), 0, 100)

        Notes:
        - Keep T (SCORE_TOLERANCE_SECONDS) declared a priori.
        - This function assumes compare() already produced absolute errors (seconds)
        and per-mic weights (from confidence).
        """

        per_mic = comparison.get("per_mic", {})
        if len(per_mic) < MIN_MICS_REQUIRED:
            return 0.0

        total_weight = 0.0
        total_weighted_absolute_error = 0.0

        for mic_name, mic_result in per_mic.items():
            absolute_error_seconds = float(mic_result.get("absolute_error_s", 0.0))
            mic_weight = float(mic_result.get("weight", 1.0))

            total_weight += mic_weight
            total_weighted_absolute_error += mic_weight * absolute_error_seconds

        if total_weight <= 0.0:
            return 0.0

        weighted_mean_absolute_error = total_weighted_absolute_error / total_weight

        tolerance = float(SCORE_TOLERANCE_SECONDS)
        if tolerance <= 0.0:
            return 0.0

        raw_score = 100.0 * (1.0 - (weighted_mean_absolute_error / tolerance))

        # clamp to 0..100
        if raw_score < 0.0:
            return 0.0
        if raw_score > 100.0:
            return 100.0
        return float(raw_score)