# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.types import PropertyGroup, AddonPreferences
from bpy.props import IntProperty, StringProperty, BoolProperty, CollectionProperty, PointerProperty
from bpy.utils import register_class, unregister_class


class BLENDFINALS_PG_instructions(PropertyGroup):
    command: StringProperty()


class BLENDFINALS_PG_student(PropertyGroup):
    student_name: StringProperty()
    correct_answer: StringProperty()


def ensure_unique_test_name(self, context):
    existing_labels = [item.label for item in context.scene.blendfinals.tests if item.as_pointer() != self.as_pointer()]

    if self.label in existing_labels:
        base_name = self.label
        suffix = 1
        new_name = f"{base_name}.{suffix:03}"

        while new_name in existing_labels:
            suffix += 1
            new_name = f"{base_name}.{suffix:03}"

        self.label = new_name


class BLENDFINALS_PG_test(PropertyGroup):
    label: StringProperty(default="Name", update=ensure_unique_test_name)
    description: StringProperty(default="Description")
    date: StringProperty(default="")
    auto: BoolProperty(default=False, name="Run All", description="Include in Run All")
    instructions: CollectionProperty(type=BLENDFINALS_PG_instructions)
    students: CollectionProperty(type=BLENDFINALS_PG_student)


def record_active_updater(self, context):
    selected_names = [obj.name for obj in context.selected_objects]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern=bpy.context.active_object.name, extend=False)
    for name in selected_names:
        bpy.ops.object.select_pattern(pattern=name)


class BLENDFINALS_PG_properties(PropertyGroup):
    index_tests: IntProperty(default=0)
    test_result: StringProperty()
    tests: CollectionProperty(type=BLENDFINALS_PG_test)
    is_testing: BoolProperty()
    record_button_label: StringProperty(default="Record New")
    record_active: BoolProperty(name="Record Active", update=record_active_updater)


class BLENDFINALS_AddonPreferences(AddonPreferences):
    bl_idname = 'BlendFinals'
    
    saved_tests: CollectionProperty(type=BLENDFINALS_PG_test)

    def draw(self, context):
        layout = self.layout
        layout.label(text="BlendFinals Saved Tests")
        for test in self.saved_tests:
            box = layout.box()
            box.label(text=test.label)
            box.label(text=test.description)


classes = [
    BLENDFINALS_PG_instructions,
    BLENDFINALS_PG_student,
    BLENDFINALS_PG_test,
    BLENDFINALS_PG_properties,
    BLENDFINALS_AddonPreferences,
]


def register():
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.blendfinals = PointerProperty(type=BLENDFINALS_PG_properties)


def unregister():
    del bpy.types.Scene.blendfinals
    for cls in reversed(classes):
        unregister_class(cls)