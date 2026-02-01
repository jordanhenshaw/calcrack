# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.types import PropertyGroup
from bpy.props import IntProperty, StringProperty, PointerProperty, FloatProperty
from bpy.utils import register_class, unregister_class

SPEED_SOUND_IN_FPS = 1126


class CALCRACK_PG_scene(PropertyGroup):
    total_score: StringProperty(default="Name")


classes = [
    CALCRACK_PG_scene,
]


def register():
    bpy.types.Object.confidence = IntProperty(name="Confidence", default=3, min=1, max=3)
    bpy.types.Object.delta_t = FloatProperty(name="Delta T", default=0, min=0, max=100)

    bpy.types.Object.ammo_speed = IntProperty(name="Projectile Speed", description="Velocity of round in Feet per Second (FPS)", default=1600, min=SPEED_SOUND_IN_FPS, max=100000)
    bpy.types.Object.rifle_accuracy = FloatProperty(name="Accuracy", description='''Rifle's accuracy score on 0-100 scale.''', default=0, min=0, max=100)
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.calcrack = PointerProperty(type=CALCRACK_PG_scene)


def unregister():
    del bpy.types.Scene.calcrack
    for cls in reversed(classes):
        unregister_class(cls)