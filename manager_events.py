# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.app.handlers import persistent

from .algorithm.algorithm import Algorithm

_IS_RUNNING = False


def fire_all_rifles(scene):
    if not bpy.context.scene.calcrack.live_update:
        return
    
    all_rifles = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and obj.aim_target]
    for rifle in all_rifles:
        Result = Algorithm(scene, rifle).execute()
        rifle.aggregated_errors = Result.aggregated_errors
        rifle.mean_error = Result.mean_error


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