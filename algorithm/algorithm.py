# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from .wrap_delta_t import calculate_crack_thump

FPS_TO_MPS = 0.3048  # feet/sec -> meters/sec


class Algorithm:
    '''
    Context: We need to find out where a bullet was fired from. All we have is a bunch of non-time-synced audio recordings of a crack and thump.

    Problem: We need to test candidate shooting position/angle/speed solutions. We need to see if a possible solution would actually create the
    crack-thump delta-t times for each microphone, the ones we actually observe in the recordings.

    Solution: We must mathematically calculate the mach cone, predict what the crack-thump delay should be, and later check how close the actual
    delay is.

    Final Output: We add up all the errors in seconds and return that to the user.
    '''
    def __init__(self, context, ao):
        self.context = context
        self.rifle = ao

        self.round_velocity_fps = self.rifle.ammo_speed
        self.rifle_origin_world = self.rifle.matrix_world.translation.copy()
        self.bullet_speed_mps = float(self.round_velocity_fps) * FPS_TO_MPS
        self.rifle_endpoint = ao.aim_target.location

        # print(f"Velocity (FPS): {self.round_velocity}")
        # print(f"Mic Data: {self.mic_data}")
        # print(f"Rifle origin (world): {self.rifle_origin_world}")
        # print(f"Rifle endpoint (display): {self.rifle_endpoint}")

    def get_rifle_endpoint(self, obj):
        return obj.aim_target.location


    def execute(self):
        actual = self.get_all_mic_data()
        predictions = self.predict_mic_delta_ts(actual)
        return self.compare(actual, predictions)
    
    def get_all_mic_data(self):
        all_mics = [
            obj for obj in bpy.context.scene.objects
            if obj.type == 'CAMERA' and obj.delta_t != 0.0
        ]

        mic_data = {}
        for mic in all_mics:
            mic_data[mic.name] = (mic.location.copy(), round(mic.delta_t, 3), mic.confidence)
        return mic_data
    
    def predict_mic_delta_ts(self, actual):
        predictions = {}

        for mic_name, (mic_position, _, _) in actual.items():
            predictions[mic_name] = calculate_crack_thump(self.rifle_origin_world, self.rifle_endpoint, self.round_velocity_fps, mic_position)

        return predictions

    def compare(self, actual, predictions):
        total_error = 0.0

        for mic_name, (_, actual_dt, _) in actual.items():
            pred_dt = predictions.get(mic_name)
            if pred_dt is None:
                continue
            total_error += abs(float(pred_dt) - float(actual_dt))

        return round(total_error, 3)