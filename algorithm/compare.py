# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from ..maintenance.debug import debug_each


def compare(actual, predictions):
        scene = bpy.context.scene # Keep these expensive bpy calls outside loop
        is_printing = scene.calcrack.print_to_terminal
        error_margin = scene.calcrack.error_margin

        errors = []
        for mic_name, (_, actual_dt, _) in actual.items():
            pred_dt = predictions.get(mic_name)
            if pred_dt is None:
                continue
            error = abs(float(pred_dt) - float(actual_dt))
            error = apply_margin_error(error, error_margin)
            errors.append(error)
            if is_printing: debug_each(mic_name, error, actual_dt, pred_dt)
        
        sum_errors = round(sum(errors), 3)
        mean = sum_errors / len(errors)

        return sum_errors, mean


def apply_margin_error(error, margin):
     '''If you change this, you MUST update the tooltip for scene Error Margin!!!'''
     if round(error, 3) <= margin:
          return 0.00
     return error