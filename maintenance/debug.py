# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from .rainbow import *


def debug_main(Algorithm):
    if not bpy.context.scene.calcrack.print_to_terminal:
        return
    
    print(f"\n{BLUE}#########################\n# Firing...\n#########################")
    print(f"{BLUE}Velocity (FPS): {RESET}{Algorithm.round_velocity_fps}")
    print(f"{BLUE}Rifle origin: {RESET}{tuple(round(v, 2) for v in Algorithm.rifle_origin_world)}")
    print(f"{BLUE}Rifle endpoint: {RESET}{tuple(round(v, 2) for v in Algorithm.rifle_endpoint)}")


def debug_each(mic_name, error, actual_dt, pred_dt):
    # Return early for scene toggle outside loop
    print(f"{BLUE}Error: {RED}{error:.2f}s{BLUE}. Actual: {RESET}{actual_dt:.2f}s{BLUE}. Predicted: {RESET}{pred_dt:.2f}s{BLUE}.{RESET} ---> {RESET}{mic_name}")