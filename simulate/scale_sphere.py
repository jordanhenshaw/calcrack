# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later


def get_sphere_final_scale(self):
    duration_flight = self.Algorithm.rifle.duration_flight  # seconds
    c = self.Algorithm.speed_sound_mps
    sound_radius = duration_flight * c
    return sound_radius