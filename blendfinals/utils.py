# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later


def register_class(cls):
    from .data import _register_class
    _register_class(cls)


def unregister_class(cls):
    from .data import _unregister_class
    _unregister_class(cls)