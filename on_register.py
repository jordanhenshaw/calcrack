# SPDX-FileCopyrightText: 2025 Alva Theaters
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

from . import blendfinals
from bpy.app.handlers import persistent


def assert_directory_name():
    pass


def assert_no_duplicates():
    pass


def assert_blender_version():
    pass


def append_blendfinals():
    sys.modules['blendfinals'] = blendfinals
    sys.modules['blendfinals.utils'] = blendfinals.utils
    sys.modules['blendfinals.rainbow'] = blendfinals.rainbow


@persistent
def load_ui_list(dummy1=None, dummy2=None):
    import bpy

    scene = bpy.context.scene
    if not hasattr(scene, "blendfinals"):
        return

    prefs = bpy.context.preferences.addons['BlendFinals'].preferences
    scene_tests = scene.blendfinals.tests

    if not prefs.saved_tests:
        return

    scene_tests.clear()

    for saved_test in prefs.saved_tests:
        test = scene_tests.add()
        test.label = saved_test.label
        test.description = saved_test.description
        test.date = saved_test.date
        test.auto = saved_test.auto

        if hasattr(saved_test, "commands"):
            for saved_cmd in saved_test.commands:
                cmd = test.commands.add()
                cmd.command = saved_cmd.command

    scene.blendfinals.index_tests = 0