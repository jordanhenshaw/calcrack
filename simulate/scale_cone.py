# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later


def get_cone_final_scale(self):
    duration_flight = self.Algorithm.rifle.duration_flight  # seconds
    v = self.Algorithm.bullet_speed_mps

    bullet_distance = (duration_flight * v) / 2 # meters
    return bullet_distance