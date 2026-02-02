# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

import math


def calculate(x, r, R_mag, v, c):
    """
    x      : distance along bullet path (m)
    r      : perpendicular distance to path (m)
    R_mag  : distance from muzzle to mic (m)
    v      : bullet speed (m/s)
    c      : speed of sound (m/s)
    """
    t_thump = R_mag / c
    t_crack = (x + r * math.sqrt(v*v - c*c) / c) / v
    return t_thump - max(t_crack, 0.0)
