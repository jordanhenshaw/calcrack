# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

from .calculate_delta_t import calculate
SPEED_OF_SOUND_IN_MPS = 343
FPS_TO_MPS = 0.3048


def calculate_crack_thump(rifle_origin_world, rifle_endpoint, round_velocity_fps, mic_position):
    origin = rifle_origin_world
    endpoint = rifle_endpoint

    # Bullet direction (Blender space)
    d = endpoint - origin
    if d.length == 0:
        return 0.0
    d.normalize()

    # Convert units
    v = float(round_velocity_fps * FPS_TO_MPS)   # m/s
    c = float(SPEED_OF_SOUND_IN_MPS)

    # Relative mic position
    R = mic_position - origin

    # Geometry decomposition
    x = R.dot(d)                  # along-path distance (m)
    R_perp = R - d * x
    r = R_perp.length             # perpendicular distance (m)
    R_mag = R.length              # muzzle → mic distance (m)

    return float(calculate(x, r, R_mag, v, c))