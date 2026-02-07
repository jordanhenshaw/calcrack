# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Panel

RIFLE_TYPE = 'SINGLE_ARROW'
MIC_TYPE = 'MIC_TYPE'
TARGET_TYPE = 'TARGET_TYPE'


class CalcrackBase:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Calcrack'

    @classmethod
    def poll(cls, context):
        return (
            hasattr(context, 'scene') and
            hasattr(context, 'active_object') and
            context.active_object
        )


class CALCRACK_PT_object_ui(Panel, CalcrackBase):
    bl_label = "Object"
    
    def draw(self, context):
        ao = context.active_object

        object_type = find_object_type(ao)

        if object_type == RIFLE_TYPE:
            draw_rifle_ui(self, ao)
        elif object_type == MIC_TYPE:
            draw_mic_ui(self, ao)
        elif object_type == TARGET_TYPE:
            draw_target_ui(self, ao)


class CALCRACK_PT_settings_ui(Panel, CalcrackBase):
    bl_label = "Settings"
    
    def draw(self, context):
        row = self.layout.row()
        row.prop(context.scene.calcrack, 'temp_f')

        row = self.layout.row()
        row.prop(context.scene.calcrack, 'error_margin')

        row = self.layout.row()
        row.label(text=f"Aggregated Error (Sim): {round(context.scene.calcrack.aggregated_errors, 3)}")

        row = self.layout.row()
        row.label(text=f"Mean Error (Sim): {round(context.scene.calcrack.mean_error, 3)}")

        row = self.layout.row()
        row.prop(context.scene.calcrack, 'print_to_terminal')

        row = self.layout.row()
        row.prop(context.scene.calcrack, 'live_update')


def find_object_type(ao):
    if ao.type not in ['MESH', 'CAMERA', 'EMPTY']:
        return
    elif ao.type == 'MESH':
        return RIFLE_TYPE
    elif ao.type == 'CAMERA':
        return MIC_TYPE
    elif ao.type == 'EMPTY':
        return TARGET_TYPE
    

def draw_rifle_ui(self, ao):
    layout = self.layout

    row = layout.row()
    row.label(text="Rifle")

    row = self.layout.row()
    row.prop(ao, 'name', text="Name")

    layout = self.layout
    row = layout.row()

    row.prop_search(
        ao,
        "aim_target",
        bpy.data,
        "objects",
        text="Target"
    )

    row = self.layout.row()
    row.prop(ao, 'ammo_speed', text="Speed (FPS)")

    row = self.layout.row()
    row.operator('calcrack.rifle_fire')

    row = self.layout.row()
    row.label(text=f"Aggregated Error: {round(ao.aggregated_errors, 3)}s.")

    row = self.layout.row()
    row.label(text=f"Mean Error: {round(ao.mean_error, 3)}s.")

    row = self.layout.row()
    row.operator('calcrack.rifle_simulate')

    row = self.layout.row()
    row.prop(ao, 'duration_flight')


def draw_mic_ui(self, ao):
    layout = self.layout

    row = layout.row()
    row.label(text="Microphone")

    row = self.layout.row()
    row.prop(ao, 'name', text="Name")
    
    row = self.layout.row()
    row.prop(ao, 'confidence', text="Confidence")

    row = self.layout.row()
    row.prop(ao, 'delta_t', text="Delta T")

    row = layout.row()
    row.label(text="Simulation Set Points")

    row = self.layout.row()
    row.label(text=f"Crack: {round(ao.time_crack, 3)}; Thump: {round(ao.time_thump, 3)}")

    row = self.layout.row()
    row.operator('calcrack.crack_set')
    row.operator('calcrack.thump_set')

    row = self.layout.row()
    row.label(text=f"Simulation Delta T: {round(ao.time_thump - ao.time_crack, 3)}")


def draw_target_ui(self, ao):
    layout = self.layout

    row = layout.row()
    row.label(text="Target")

    row = self.layout.row()
    row.prop(ao, 'name', text="Name")

    for obj in bpy.context.scene.objects:
        if not hasattr(obj, 'aim_target'):
            continue
        if not obj.aim_target:
            continue
        if obj.aim_target is not ao:
            continue
        
        box = self.layout.box()
        row = box.row()
        row.label(text=f'''Rifle "{obj.name}"''')

        row = box.row()
        row.prop(obj, 'ammo_speed', text="Speed (FPS)")

        row = box.row()
        row.label(text=f"Aggregated Error: {round(obj.aggregated_errors, 3)}s.")

        row = box.row()
        row.label(text=f"Mean Error: {round(obj.mean_error, 3)}s.")


classes = [
    CALCRACK_PT_object_ui,
    CALCRACK_PT_settings_ui
]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)