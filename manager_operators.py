# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.types import Operator
from bpy.utils import register_class, unregister_class

from .algorithm.algorithm import Algorithm
    

class CALCRACK_OT_rifle_fire(Operator):
    '''Press to test the accuracy of the current rifle's shooting angle and round's velocity against the actual mircophone's crack-thump delta-t's'''
    bl_idname = 'calcrack.rifle_fire'
    bl_label = "Fire"

    def execute(self, context):
        ao = context.active_object
        aggregated_error, mean_error = Algorithm(context.scene, ao).execute()
        ao.aggregated_errors = aggregated_error
        ao.mean_error = mean_error
        self.report({'INFO'}, f"Aggregated Error: {aggregated_error}s. Mean Error: {mean_error}s.")
        return {'FINISHED'}
    
    
classes = [
    CALCRACK_OT_rifle_fire,
]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)