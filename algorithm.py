# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import bpy
from bpy.types import PropertyGroup
import difflib

from .blendfinals.rainbow import *
from .command_rewriter import BlenderCommandRewriter


class Algorithm:
    def __init__(self, context):
        import blendfinals
        self.TestClasses = blendfinals.data.test_subjects
        self.scene = context.scene.blendfinals


    def start_recording(self):
        for Test in self.TestClasses.values():
            Test.start_recording()

        clear_info_editor()


    def end_recording(self):
        scene = self.scene

        if not (raw := copy_info_reports_from_editor()):
            return
        
        command_list = split_lines(raw)

        active_test = scene.tests[scene.index_tests]
        active_test.label = f"Test {len(scene.tests)}"
        active_test.instructions.clear()
        for cmd in command_list:
            cmd_item = active_test.instructions.add()
            cmd_item.command = cmd

        for Test in self.TestClasses.values():
            new_student = active_test.students.add()
            new_student.student_name = Test.bf_idname
            new_student.correct_answer = Test.end_recording()

        return "Successfully recorded test"

    
    def save(self, index) -> PropertyGroup:
        test = self.scene.tests[index]
        prefs = bpy.context.preferences.addons['BlendFinals'].preferences
        new_test = prefs.saved_tests.add()
        new_test.label = test.label
        new_test.description = test.description
        new_test.date = test.date
        new_test.auto = test.auto

        # If commands exist in test object
        if hasattr(test, "instructions") and hasattr(test, "students"):
            for cmd in test.instructions:
                new_cmd = new_test.instructions.add()
                new_cmd.command = cmd.command

            import blendfinals
            TestClasses = blendfinals.data.test_subjects

            for Test in TestClasses.values():
                for student in test.students:
                    if student.student_name == Test.bf_idname:
                        new_student = new_test.students.add()
                        new_student.student_name = Test.bf_idname
                        new_student.correct_answer = Test.end_recording()

        bpy.ops.wm.save_userpref()
        return test


    def run(self, all=False):
        prefs = bpy.context.preferences.addons['BlendFinals'].preferences
        scene_tests = self.scene.tests

        results = []
        if not all:
            selected_label = scene_tests[self.scene.index_tests].label
            saved = next((t for t in prefs.saved_tests if t.label == selected_label), None)
            test = scene_tests[self.scene.index_tests]
            results.append(self._run_test(test))
        else:
            for scene_test in scene_tests:
                if not scene_test.auto:
                    continue
                label = scene_test.label
                saved = next((t for t in prefs.saved_tests if t.label == label), None)
                test = saved if saved else scene_test
                results.append(self._run_test(test))
        
        if not results:
            return "An error has occurred"
        
        if "Fail" in results:
            return "Test failed"
        else:
            return "Test passed"


    def _run_test(self, active_test):
        if not active_test:
            active_test = self.scene.tests[self.scene.index_tests]

        for Test in self.TestClasses.values():
            Test.start_test()

        rewriter = BlenderCommandRewriter()

        for cmd in getattr(active_test, "instructions", []):
            rewritten = rewriter.execute(cmd.command)
            run_command(rewritten)

        result_label = "Pass"
        for Test in self.TestClasses.values():
            correct_answer = None
            for student in active_test.students:
                if student.student_name == Test.bf_idname:
                    correct_answer = student.correct_answer
                    break
            if (result := Test.end_test()) != correct_answer:
                result_label = "Fail"
                print(f"""{CYAN}BlendFinals "{RESET}{active_test.label}{CYAN}" Test: {RED}Failed{RESET}""")
                report_print(result, correct_answer)
                if hasattr(Test, 'on_test_fail'):
                    Test.on_test_fail()
                
            else:
                print(f"""{CYAN}BlendFinals "{RESET}{active_test.label}{CYAN}" Test: {GREEN}Passed.{RESET}""")
        return result_label


def clear_info_editor():
    """Clear all reports from the INFO editor."""
    for area in bpy.context.screen.areas:
        if area.type == 'INFO':
            for region in area.regions:
                if region.type == 'WINDOW':
                    space = next((s for s in area.spaces if s.type == 'INFO'), None)
                    if space:
                        with bpy.context.temp_override(area=area, region=region, space_data=space):
                            try:
                                bpy.ops.info.select_all(action='SELECT')
                                bpy.ops.info.report_delete()
                                return
                            except Exception as e:
                                print(f"ERROR clearing INFO: {e}")
    print("No INFO editor is currently open to clear.")


def copy_info_reports_from_editor():
    for area in bpy.context.screen.areas:
        if area.type == 'INFO':
            for region in area.regions:
                if region.type == 'WINDOW':
                    space = next((s for s in area.spaces if s.type == 'INFO'), None)
                    if space:
                        with bpy.context.temp_override(area=area, region=region, space_data=space):
                            try:
                                bpy.ops.info.select_all(action='SELECT')
                                bpy.ops.info.report_copy()
                                return bpy.context.window_manager.clipboard
                            except Exception as e:
                                print(f"ERROR during copy: {e}")

    print("No INFO editor is currently open.")


def split_lines(raw_text):
    return [line.strip() for line in raw_text.splitlines() if line.strip().startswith("bpy.")]


def run_command(command: str):
    """
    Executes a string like 'bpy.ops.mesh.primitive_cube_add(...)'.
    Catches and prints any exceptions that occur.
    """
    try:
        if not command.strip().startswith("bpy."):
            print(f"BlendFinals: Skipping non-bpy command: {command}")
            return

        exec(command, globals())

    except Exception as e:
        print(f"BlendFinals: Failed to execute command: {command}")
        print(f"BlendFinals: Error: {e}")


def report_print(actual, expected):
    if not actual:
        print('''Blendfinals: Test is missing an "actual" value.''')
        return
    
    if not expected:
        print('''Blendfinals: Test is missing an "expected" value.''')
        return
    
    diff = '\n'.join(
        difflib.unified_diff(
            expected.splitlines(),
            actual.splitlines(),
            fromfile='expected',
            tofile='actual',
            lineterm=''
        )
    )
    print("Test answer did not match recording.\n--- Diff ---\n" + diff)