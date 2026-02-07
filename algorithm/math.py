# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

import math


def calculate(x, r, R_mag, v, c):
    """
    x      : distance along bullet path (m) from muzzle
    r      : perpendicular distance to path (m)
    R_mag  : distance from muzzle to mic (m)
    v      : bullet speed (m/s)
    c      : speed of sound (m/s)
    """
    t_thump = R_mag / c
    if v <= c:
        return 0.0

    cot_theta = math.sqrt(v*v - c*c) / c

    tan_theta = c / math.sqrt(v*v - c*c)
    if x < r * tan_theta:
        return 0.0

    t_crack = (x + r * cot_theta) / v

    if t_crack < 0.0:
        t_crack = 0.0

    return t_thump - t_crack