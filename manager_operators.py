# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.types import Operator
from bpy.utils import register_class, unregister_class

from .algorithm.algorithm import Algorithm
from .simulate.simulate import Simulate
    

class CALCRACK_OT_rifle_fire(Operator):
    '''Press to test the accuracy of the current rifle's shooting angle and round's velocity against the actual mircophone's crack-thump delta-t's'''
    bl_idname = 'calcrack.rifle_fire'
    bl_label = "Fire"

    def execute(self, context):
        ao = context.active_object
        Result = Algorithm(context.scene, ao).execute()
        ao.aggregated_errors = Result.aggregated_errors
        ao.mean_error = Result.mean_error
        self.report({'INFO'}, f"Aggregated Error: {round(Result.aggregated_errors, 3)}s. Mean Error: {round(Result.mean_error, 3)}s.")
        return {'FINISHED'}
    

class CALCRACK_OT_rifle_simulate(Operator):
    '''Press to test the accuracy of the current rifle's shooting angle with a 3D visual simulation'''
    bl_idname = 'calcrack.rifle_simulate'
    bl_label = "Simulate"

    def execute(self, context):
        ao = context.active_object
        Result = Algorithm(context.scene, ao).execute()
        Simulate(context.scene, ao, Result).execute()
        self.report({'INFO'}, f"Mach cone and bang simulations added. Press play to begin setting C/T points on each microphone.")
        return {'FINISHED'}
    

class CALCRACK_OT_crack_set(Operator):
    '''Press when the simulated mach cone intersects this microphone's diaphragm'''
    bl_idname = 'calcrack.crack_set'
    bl_label = "Set Crack"

    def execute(self, context):
        ao = context.active_object
        ao.time_crack = context.scene.frame_current * .001
        calculate_scene_simulation_errors(context)
        self.report({'INFO'}, f"Set microphone's crack time to {context.scene.frame_current}")
        return {'FINISHED'}
    

class CALCRACK_OT_thump_set(Operator):
    '''Press when the simulated bang sphere intersects this microphone's diaphragm'''
    bl_idname = 'calcrack.thump_set'
    bl_label = "Thump"

    def execute(self, context):
        ao = context.active_object
        ao.time_thump = context.scene.frame_current * .001
        calculate_scene_simulation_errors(context)
        self.report({'INFO'}, f"Set microphone's thump time to {context.scene.frame_current}")
        return {'FINISHED'}
    

def calculate_scene_simulation_errors(context):
    all_mics = [
        obj for obj in context.scene.objects
        if obj.type == 'CAMERA' and obj.delta_t != 0.0
    ]

    aggregated_errors = []
    for mic in all_mics:
        pred_dt = mic.time_thump - mic.time_crack
        actual_dt = mic.delta_t
        aggregated_errors.append(abs(pred_dt - actual_dt))

    aggr = round(sum(aggregated_errors), 3)
    mean = aggr / len(all_mics)

    context.scene.calcrack.aggregated_errors = aggr
    context.scene.calcrack.mean_error = mean


    
classes = [
    CALCRACK_OT_rifle_fire,
    CALCRACK_OT_rifle_simulate,
    CALCRACK_OT_crack_set,
    CALCRACK_OT_thump_set
]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)