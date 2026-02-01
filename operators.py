# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.types import Operator
from bpy.utils import register_class, unregister_class

from .algorithm import Algorithm

from .ui import RIFLE_TYPE
    

class CALCRACK_OT_rifle_fire(Operator):
    '''Press to test the accuracy of the current rifle's shooting angle and round's velocity against the actual mircophone's crack-thump delta-t's'''
    bl_idname = 'calcrack.rifle_fire'
    bl_label = "Fire"

    def execute(self, context):
        ao = context.active_object
        accuracy_score = Algorithm(context, ao).execute()
        ao.rifle_accuracy = accuracy_score
        self.report({'INFO'}, f"Current rifle and position scores {accuracy_score}%")
        return {'FINISHED'}


class CALCRACK_OT_all_rifles_fire(Operator):
    '''Press to test the accuracy of the all rifle's shooting angles and round's velocities against the actual mircophone's crack-thump delta-t's'''
    bl_idname = 'calcrack.all_rifles_fire'
    bl_label = "Fire All"

    def execute(self, context):
        all_rifles = [empty for empty in bpy.context.scene.objects if empty.type == 'EMPTY' and empty.empty_display_type == RIFLE_TYPE]
        for rifle in all_rifles:
            accuracy_score = Algorithm(context, rifle).execute()
            rifle.rifle_accuracy = accuracy_score
        return {'FINISHED'}
    
    
classes = [
    CALCRACK_OT_rifle_fire,
    CALCRACK_OT_all_rifles_fire
]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)