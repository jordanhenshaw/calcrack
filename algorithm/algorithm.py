# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

from .wrap import calculate_crack_thump
from ..maintenance.debug import debug_main
from .compare import compare

FPS_TO_MPS = 0.3048


class Algorithm:
    '''
    Context: We need to find out where a bullet was fired from. All we have is a bunch of non-time-synced audio recordings of a crack and thump.

    Problem: We need to test candidate shooting position/angle/speed solutions. We need to see if a possible solution would actually create the
    crack-thump delta-t times for each microphone, the ones we actually observe in the recordings.

    Solution: We must mathematically calculate the mach cone, predict what the crack-thump delay should be, and later check how close the actual
    delay is.

    Final Output: We add up all the errors in seconds and return that to the user.
    '''
    def __init__(self, scene, ao):
        self.scene = scene
        self.rifle = ao

        self.temp_f = scene.calcrack.temp_f
        self.round_velocity_fps = self.rifle.ammo_speed
        self.rifle_origin_world = self.rifle.matrix_world.translation.copy()
        self.bullet_speed_mps = float(self.round_velocity_fps) * FPS_TO_MPS
        self.rifle_endpoint = ao.aim_target.matrix_world.translation.copy()

        debug_main(self)


    def execute(self):
        actual = self.get_all_mic_data()
        predictions = self.predict_mic_delta_ts(actual)
        return compare(actual, predictions)
    
    def get_all_mic_data(self):
        all_mics = [
            obj for obj in self.scene.objects
            if obj.type == 'CAMERA' and obj.delta_t != 0.0
        ]

        mic_data = {}
        for mic in all_mics:
            mic_position = mic.matrix_world.translation.copy()
            mic_data[mic.name] = (mic_position, round(mic.delta_t, 3), mic.confidence)
        return mic_data
    
    def predict_mic_delta_ts(self, actual):
        predictions = {}

        for mic_name, (mic_position, _, _) in actual.items():
            predictions[mic_name] = calculate_crack_thump(self.rifle_origin_world, self.rifle_endpoint, self.round_velocity_fps, mic_position, self.temp_f)

        return predictions