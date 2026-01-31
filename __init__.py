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
    "version": (1, 1, 0),
    "blender": (4, 4, 1),
    "description": "Crack-thump acoustic analysis.",
    "category": "Science",
}

import bpy

from .on_register import (
    assert_directory_name, 
    assert_no_duplicates, 
    assert_blender_version, 
    append_blendfinals,
    load_ui_list
)


def register():
    from .register_bpy_data import register
    assert_directory_name()
    assert_no_duplicates()
    assert_blender_version()
    append_blendfinals()
    register()
    bpy.app.timers.register(load_ui_list, first_interval=.01)
    bpy.app.handlers.load_post.append(load_ui_list)


def unregister():
    bpy.app.handlers.load_post.remove(load_ui_list)
    from .register_bpy_data import unregister
    unregister()