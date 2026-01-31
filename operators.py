# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.types import Operator
from bpy.props import IntProperty
from bpy.utils import register_class, unregister_class

from .algorithm import Algorithm


class BLENDFINALS_OT_test_record(Operator):
    '''
    Record a test by interacting with your add-on through the UI. 
    Import blendfinals directly and use blendfinals.utils.input() 
    to tell BlendFinals what your add-on is doing. It only takes 
    one parameter, which can be string, int, or float.
    '''
    bl_idname = 'blendfinals.test_record'
    bl_label = "Record"

    def execute(self, context):
        result = ""
        scene = context.scene.blendfinals

        info_editors = [area for area in context.screen.areas if area.type == 'INFO']

        if not info_editors:
            self.report({'ERROR'}, "Open an Info editor")
            return {'CANCELLED'}

        if not scene.is_testing:
            new_test = scene.tests.add()
            new_test.label = ""
            new_test.description = "Recorded manually."
            scene.index_tests = len(scene.tests) - 1
            self.report({'INFO'}, "Started Recording.")
            scene.record_button_label = "Recording"
            Algorithm(context).start_recording()
        else:
            self.report({'INFO'}, "Stopped recording.")
            scene.record_button_label = "Record New"
            result = Algorithm(context).end_recording()

        scene.is_testing = not scene.is_testing

        if result:
            self.report({'INFO'}, result)

        return {'FINISHED'}
    

class BLENDFINALS_OT_test_save(Operator):
    '''Save test.'''
    bl_idname = 'blendfinals.test_save'
    bl_label = "Save"

    def execute(self, context):
        scene = context.scene.blendfinals
        index = scene.index_tests
        if not (0 <= index < len(scene.tests)):
            self.report({'WARNING'}, "No valid test selected.")
            return {'CANCELLED'}

        test = Algorithm(context).save(index)
        self.report({'INFO'}, f"Saved test '{test.label}' to preferences.")
        return {'FINISHED'}
    

class BLENDFINALS_OT_test_run(Operator):
    '''Run test.'''
    bl_idname = 'blendfinals.test_run'
    bl_label = "Run"

    def execute(self, context):
        props = context.scene.blendfinals

        if not props.tests or props.index_tests >= len(props.tests):
            self.report({'WARNING'}, "No valid test selected.")
            return {'CANCELLED'}

        result = Algorithm(context).run()
        self.report({'INFO'}, result)
        return {'FINISHED'}


class BLENDFINALS_OT_test_delete(Operator):
    '''Delete test.'''
    bl_idname = 'blendfinals.test_delete'
    bl_label = "Delete"
    options = {'UNDO'}

    def execute(self, context):
        props = context.scene.blendfinals
        index = props.index_tests

        if not (0 <= index < len(props.tests)):
            self.report({'WARNING'}, "No test selected.")
            return {'CANCELLED'}

        test = props.tests[index]
        label_to_delete = test.label

        props.tests.remove(index)
        props.index_tests = max(0, index - 1)

        addon_name = 'BlendFinals'.split('.')[0]
        prefs = bpy.context.preferences.addons.get(addon_name)
        if prefs:
            prefs = prefs.preferences
            for i, saved in enumerate(prefs.saved_tests):
                if saved.label == label_to_delete:
                    prefs.saved_tests.remove(i)
                    break

        bpy.ops.wm.save_userpref()
        self.report({'INFO'}, f"Deleted test '{label_to_delete}'.")
        return {'FINISHED'}


class BLENDFINALS_OT_test_bump(Operator):
    '''Bump test up or down.'''
    bl_idname = 'blendfinals.test_bump'
    bl_label = "Bump"

    direction: IntProperty()  # +1 for down, -1 for up

    def execute(self, context):
        props = context.scene.blendfinals
        idx = props.index_tests
        new_idx = idx + self.direction

        if not (0 <= idx < len(props.tests)):
            self.report({'WARNING'}, "Invalid index.")
            return {'CANCELLED'}

        if not (0 <= new_idx < len(props.tests)):
            self.report({'WARNING'}, "Can't move further.")
            return {'CANCELLED'}

        props.tests.move(idx, new_idx)
        props.index_tests = new_idx
        return {'FINISHED'}
    

class BLENDFINALS_OT_tests_all(Operator):
    '''Run all tests.'''
    bl_idname = 'blendfinals.tests_all'
    bl_label = "Run All"

    def execute(self, context):
        props = context.scene.blendfinals

        if not props.tests:
            self.report({'WARNING'}, "No valid test exists.")
            return {'CANCELLED'}

        result = Algorithm(context).run(all=True)
        self.report({'INFO'}, result)
        return {'FINISHED'}


class BLENDFINALS_OT_dump_test_to_text(Operator):
    '''Dump the selected test's commands into a new text editor block.'''
    bl_idname = 'blendfinals.dump_test_to_text'
    bl_label = "Dump to Text Block"

    def execute(self, context):
        props = context.scene.blendfinals
        index = props.index_tests

        if not (0 <= index < len(props.tests)):
            self.report({'WARNING'}, "No valid test selected.")
            return {'CANCELLED'}

        selected_label = props.tests[index].label
        prefs = bpy.context.preferences.addons['BlendFinals'].preferences
        test = next((t for t in prefs.saved_tests if t.label == selected_label), None)

        if not test:
            test = props.tests[index]

        lines = [cmd.command for cmd in test.instructions]
        content = "\n".join(lines)

        name = f"Test_{test.label}"
        if name in bpy.data.texts:
            text = bpy.data.texts[name]
            text.clear()
        else:
            text = bpy.data.texts.new(name)

        text.write(content)
        self.report({'INFO'}, f"Test '{test.label}' dumped to Text Editor as '{name}'.")
        return {'FINISHED'}
    

class BLENDFINALS_OT_test_import_from_text(Operator):
    '''Replace the active test's instructions with active Text Editor block.'''
    bl_idname = 'blendfinals.test_import_from_text'
    bl_label = "Import to Replace"

    def execute(self, context):
        scene = context.scene.blendfinals
        text = context.space_data.text

        if not text:
            self.report({'WARNING'}, "No active text block found.")
            return {'CANCELLED'}

        command_list = [line.body.strip() for line in text.lines if line.body.strip().startswith("bpy.")]
        if not command_list:
            self.report({'WARNING'}, "No valid bpy.* commands found.")
            return {'CANCELLED'}

        test_to_replace = scene.tests[scene.index_tests]
        test_to_replace.instructions.clear()

        for cmd in command_list:
            cmd_item = test_to_replace.instructions.add()
            cmd_item.command = cmd

        self.report({'INFO'}, f"Replaced {test_to_replace.label}'s instructions with {len(command_list)} command(s).")

        return {'FINISHED'}
    

classes = [
    BLENDFINALS_OT_test_record,
    BLENDFINALS_OT_test_save,
    BLENDFINALS_OT_test_run,
    BLENDFINALS_OT_test_delete,
    BLENDFINALS_OT_test_bump,
    BLENDFINALS_OT_tests_all,
    BLENDFINALS_OT_dump_test_to_text,
    BLENDFINALS_OT_test_import_from_text
]


def register():
    for cls in classes:
        register_class(cls)


def unregister():
    for cls in reversed(classes):
        unregister_class(cls)