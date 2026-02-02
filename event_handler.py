# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.app.handlers import persistent

_IS_RUNNING = False


def fire_all_rifles(scene):
    bpy.ops.calcrack.all_rifles_fire()


@persistent
def depsgraph_update_handler(scene, depsgraph):
    global _IS_RUNNING
    if _IS_RUNNING:
        return

    _IS_RUNNING = True
    try:
        fire_all_rifles(scene)
    finally:
        _IS_RUNNING = False


def register():
    if depsgraph_update_handler not in bpy.app.handlers.depsgraph_update_pre:
        bpy.app.handlers.depsgraph_update_pre.append(depsgraph_update_handler)


def unregister():
    if depsgraph_update_handler in bpy.app.handlers.depsgraph_update_pre:
        bpy.app.handlers.depsgraph_update_pre.remove(depsgraph_update_handler)