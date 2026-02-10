# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later


def get_cone_final_scale(self):
    duration_flight_s = self.Algorithm.rifle.duration_flight
    speed_bullet_mps = self.Algorithm.bullet_speed_mps
    scale_cone = duration_flight_s * speed_bullet_mps
    return scale_cone / 2  # Delete trailing half of cone behind muzzle blast.