# SPDX-FileCopyrightText: 2025 Alva Theaters
#
# SPDX-License-Identifier: GPL-3.0-or-later
# pyright: reportInvalidTypeForm=false

import re

SELECT_RE = re.compile(
    r'bpy\.ops\.object\.select_pattern\([^)]*pattern\s*=\s*["\']([^"\']+)["\']',
    re.IGNORECASE,
)
CTX_PREFIX_RE = re.compile(r'^(\s*)bpy\.context\.object\b')


class BlenderCommandRewriter:
    '''
    Context: We use Info editor as a sort of camera to remember what the user did so we can repeat
    their steps later automatically during the test cycle. But the Info editor kind of sucks as a
    camera. It has a ton of blind spots that can dramatically alter our memory of what the user did.
    
    Problem: Blender is a big meany baby when it comes to getting the Info editor to track active object.

    So we start with something like this Info editor output, which doesn't work because just cuz we 
    selected Cone.008 doesn't mean Blender is going to change bpy.context.object to Cone.008:
    
        bpy.ops.object.select_pattern(pattern="Cone.008", extend=False)
        bpy.context.object.color_profile_enum = 'option_rgbw'

    To brute force Blender into submission, we yank out the Cone.008 part and yeet it in front of the 
    .color_profile_enum = 'option_rgbw' part. Because during the test, Blender doesn't realize we want 
    the bpy.context.object to change. So we stop using bpy.context.object altogether. 

    And so this BlenderCommandRewriter code turns the above into something like below, which executes 
    during the test's run cycle as intended. The select_pattern call stores the name of the object that
    was active during the recording, and so we yank that out and yeet it into the command directly after:

        bpy.ops.object.select_pattern(pattern="Cone.008", extend=False)
        bpy.context.scene.objects['Cone.008'].color_profile_enum = 'option_rgbw'

    Remember: The test cycle's ONLY instructions are what's put into Info editor during the recording. If 
    the instructions there are not explicit enough to tell Blender exactly what to do, the test will fail
    right out of the box. Here, we kind of have to hack a solution to something the Info editor MUST record
    but doesn't.
    '''
    def __init__(self):
        self._last_selected_name = None


    def execute(self, line: str) -> str:
        """
        - If line is a select_pattern(... pattern="Something" ...), remember "Something".
        - If line starts with bpy.context.object, rewrite it to bpy.context.objects["Something"].
        - Otherwise, return line unchanged.
        """
        m = SELECT_RE.search(line)
        if m:
            self._last_selected_name = m.group(1)

        if self._last_selected_name:
            m2 = CTX_PREFIX_RE.match(line)
            if m2:
                indent = m2.group(1)
                line = CTX_PREFIX_RE.sub(
                    f'{indent}bpy.context.scene.objects["{self._last_selected_name}"]',
                    line,
                    count=1,
                )
        return line