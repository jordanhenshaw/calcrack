# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

import math

BALLISTIC_COEFF = 0.45
BULLET_MASS_GRAINS = 150.0
BULLET_DIAMETER_INCH = 0.308
AIR_DENSITY_KG_M3 = 1.225

GRAINS_TO_KG = 0.00006479891
INCH_TO_M = 0.0254


def bullet_mass_kg():
    return BULLET_MASS_GRAINS * GRAINS_TO_KG


def bullet_diameter_m():
    return BULLET_DIAMETER_INCH * INCH_TO_M


def bullet_area_m2():
    radius = bullet_diameter_m() / 2.0
    return math.pi * radius * radius


def distance_at_time(t_seconds, muzzle_velocity_mps):
    return muzzle_velocity_mps * t_seconds