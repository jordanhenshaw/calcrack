# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.types import PropertyGroup
from bpy.props import IntProperty, PointerProperty, FloatProperty, BoolProperty
from bpy.utils import register_class, unregister_class

SPEED_SOUND_IN_FPS = 1126


class CALCRACK_PG_scene(PropertyGroup):
    temp_f: IntProperty(name="Temperature (F)", default=72)
    error_margin: FloatProperty(
        name="Margin for Error (s)", 
        default=.005, 
        description="If calculated error <= this value, it will result in 0.00. Calculated error is rounded to 3 decimal points before evaluating"
    )
    print_to_terminal: BoolProperty(
        name="Print Results", 
        default=False,
        description="Run Blender from CMD (Windows) or Terminal (Mac) to see additional data printouts. WARNING: May cause lag!"
    )
    live_update: BoolProperty(name="Live Update", default=True, description="Automatically fire rifles when scene changes")


classes = [
    CALCRACK_PG_scene,
]


def register():
    bpy.types.Object.confidence = IntProperty(name="Confidence", default=3, min=1, max=3)
    bpy.types.Object.delta_t = FloatProperty(name="Delta T", default=0, min=0, max=100)

    bpy.types.Object.ammo_speed = IntProperty(name="Projectile Speed", description="Velocity of round in Feet per Second (FPS)", default=1600, min=SPEED_SOUND_IN_FPS, max=100000)
    bpy.types.Object.aim_target = PointerProperty(name="Target", type=bpy.types.Object)
    bpy.types.Object.aggregated_errors = FloatProperty(default=0, min=0, max=100)
    bpy.types.Object.mean_error = FloatProperty(default=0, min=0, max=100)
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.calcrack = PointerProperty(type=CALCRACK_PG_scene)


def unregister():
    if hasattr(bpy.types.Scene, "calcrack"):
        del bpy.types.Scene.calcrack

    for cls in reversed(classes):
        unregister_class(cls)

    for prop in (
        "mean_error",
        "aggregated_errors",
        "aim_target",
        "ammo_speed",
        "delta_t",
        "confidence",
    ):
        if hasattr(bpy.types.Object, prop):
            delattr(bpy.types.Object, prop)
