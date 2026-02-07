# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

from .math import calculate

FPS_TO_MPS = 0.3048


def calculate_crack_thump(Algorithm, mic_position_world, meters_per_bu=1.0):
    distance = find_distance(Algorithm)

    R = (mic_position_world - Algorithm.rifle_origin_world) * float(meters_per_bu)
    x = R.dot(distance)
    R_perp = R - distance * x
    r = R_perp.length
    R_mag = R.length

    return calculate(x, r, R_mag, Algorithm.bullet_speed_mps, Algorithm.speed_sound_mps)


def find_distance(Algorithm):
    rifle = Algorithm.rifle_origin_world
    target = Algorithm.rifle_endpoint
    distance = target - rifle
    return distance.normalized()