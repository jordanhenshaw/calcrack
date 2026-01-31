# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import Panel, UIList


class BLENDFINALS_PT_tests(Panel):
    '''Manual Test Recorder'''
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'BlendFinals'
    bl_label = "Tests"

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'scene')
    
    def draw(self, context):
        scene = context.scene.blendfinals
        layout = self.layout
        row = layout.row()
        
        col0 = row.column()
        col1 = row.column()
        col0.template_list(
            "BLENDFINALS_UL_tests_draw",
            "",
            context.scene.blendfinals,
            "tests",
            context.scene.blendfinals,
            "index_tests"
        )
        
        if scene.tests and not scene.is_testing:
            col1.operator("blendfinals.test_bump", text="", icon="TRIA_UP").direction = -1
            col1.operator("blendfinals.test_bump", text="", icon="TRIA_DOWN").direction = 1
            col1.operator("blendfinals.test_save", text="", icon='FILE_TICK')
            col1.operator("blendfinals.test_run", text="",icon='PLAY')
            col1.menu("BLENDFINALS_MT_test_context_menu", text="", icon='DOWNARROW_HLT')
            
        row = layout.row()
        row.alert = scene.is_testing
        row.operator("blendfinals.test_record", text=scene.record_button_label, icon='REC')
        
        if scene.tests and not scene.is_testing:
            layout.separator()

            row = layout.row()
            row.operator("blendfinals.dump_test_to_text", text="Dump to Text Block", icon='EVENT_LEFT_ARROW')

            row = layout.row()
            row.operator('blendfinals.test_import_from_text', icon='EVENT_RIGHT_ARROW')

            layout.separator()

            row = layout.row()
            row.operator("blendfinals.tests_all", text="Run All Checked", icon='CHECKBOX_HLT')
        
        else:
            layout.separator()
            
            row = layout.row()
            row.operator('blendfinals.test_import_from_text', icon='EVENT_RIGHT_ARROW')


class BLENDFINALS_PT_record_selection(Panel):
    '''Record Object Selection(s)'''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'BlendFinals'
    bl_label = "Record Selection(s)"

    @classmethod
    def poll(cls, context):
        return hasattr(context, 'scene')
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(context.scene.blendfinals, 'record_active', text="Toggle to Record Active", icon='RESTRICT_SELECT_OFF')


class BLENDFINALS_UL_tests_draw(UIList):
    bl_idname = "BLENDFINALS_UL_tests_draw"
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(item, 'label', text="", emboss=False)
            row.prop(item, 'auto', text="", expand=True)
            
            
class BLENDFINALS_MT_test_context_menu(bpy.types.Menu):
    bl_label = "Test Options"
    bl_idname = "BLENDFINALS_MT_test_context_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("blendfinals.test_delete", icon='TRASH', text="Delete Selected Test")


classes = [
    BLENDFINALS_PT_tests,
    BLENDFINALS_PT_record_selection,
    BLENDFINALS_UL_tests_draw,
    BLENDFINALS_MT_test_context_menu
]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == '__main__':  # Only for live edit
    register()