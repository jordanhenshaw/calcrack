# This file is part of Calcrack.
# Copyright (C) 2026 Jordan Henshaw

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


bl_info = {
    "name": "Calcrack",
    "author": "Jordan Henshaw",
    "location": "View3D",
    "version": (1, 0, 0),
    "blender": (4, 4, 1),
    "description": "Crack-thump acoustic analysis.",
    "category": "Science",
}

import bpy

from .manager_register import (
    assert_directory_name, 
    assert_no_duplicates, 
    assert_blender_version
)


def register():
    from .manager_register import register
    assert_directory_name()
    assert_no_duplicates()
    assert_blender_version()
    register()


def unregister():
    from .manager_register import unregister
    unregister()