# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later


def get_sphere_final_scale(self):
    duration_flight_s = self.Algorithm.rifle.duration_flight
    speed_sound_mps = self.Algorithm.speed_sound_mps
    return duration_flight_s * speed_sound_mps