# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

from .properties import register as register_properties, unregister as unregister_properties
from .operators import register as register_operators, unregister as unregister_operators
from .ui import register as register_ui, unregister as unregister_ui
from .event_handler import register as register_events, unregister as unregister_events


def register():
    register_properties()
    register_operators()
    register_ui()
    register_events()


def unregister():
    unregister_properties()
    unregister_operators()
    unregister_ui()
    unregister_events()