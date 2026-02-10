# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

import math


def find_mach_angle(Algorithm):
    return math.degrees(math.asin(Algorithm.speed_sound_mps / Algorithm.bullet_speed_mps))