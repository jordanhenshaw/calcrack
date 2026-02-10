# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later


def get_cone_orientation(self):
    rifle_location = self.Algorithm.rifle_origin_world 
    target_location = self.Algorithm.rifle_endpoint
    direction = (target_location - rifle_location)
    dir_unit = direction.normalized()
    quat = dir_unit.to_track_quat('Z', 'Y')
    return quat.to_euler(), dir_unit