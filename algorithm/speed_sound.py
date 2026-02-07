# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

KNOTS_TO_MPS = 0.51444444444


def speed_sound(temp_f):
    temp_k = (temp_f - 32) * 5/9 + 273.15
    speed_knots = 643.855 * ((temp_k/273.15) ** .5)
    speed_mps = speed_knots * KNOTS_TO_MPS
    return speed_mps