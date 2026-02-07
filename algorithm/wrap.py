# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

from .math import calculate
from .speed_sound import speed_sound

FPS_TO_MPS = 0.3048


def calculate_crack_thump(
    rifle_origin_world,
    rifle_endpoint_world,
    round_velocity_fps,
    mic_position_world,
    temp_f,
    meters_per_bu=1.0,
):
    origin = rifle_origin_world
    endpoint = rifle_endpoint_world

    d = endpoint - origin
    if d.length == 0:
        return 0.0
    d.normalize()

    v = float(round_velocity_fps) * FPS_TO_MPS
    c = speed_sound(temp_f)

    R = (mic_position_world - origin) * float(meters_per_bu)

    x = R.dot(d)
    R_perp = R - d * x
    r = R_perp.length
    R_mag = R.length

    return float(calculate(x, r, R_mag, v, c))