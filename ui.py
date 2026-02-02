# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Panel

RIFLE_TYPE = 'SINGLE_ARROW'
MIC_TYPE = 'MIC_TYPE'


class CALCRACK_PT_main_ui(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Calcrack'
    bl_label = "Calcrack Settings"

    @classmethod
    def poll(cls, context):
        return (
            hasattr(context, 'scene') and
            hasattr(context, 'active_object') and
            context.active_object
        )
    
    def draw(self, context):
        ao = context.active_object

        object_type = find_object_type(ao)

        if object_type == RIFLE_TYPE:
            draw_rifle_ui(self, ao)
        elif object_type == MIC_TYPE:
            draw_mic_ui(self, ao)
        else:
            return
        
        self.layout.separator()
        row = self.layout.row()
        row.operator('calcrack.all_rifles_fire')


def find_object_type(ao):
    if ao.type not in ['MESH', 'CAMERA']:
        return
    elif ao.type == 'MESH':
        return RIFLE_TYPE
    elif ao.type == 'CAMERA':
        return MIC_TYPE
    

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
    row.label(text=f"Error in Seconds: {round(ao.rifle_accuracy, 3)}")


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


classes = [
    CALCRACK_PT_main_ui,
]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == '__main__':  # Only for live edit
    register()