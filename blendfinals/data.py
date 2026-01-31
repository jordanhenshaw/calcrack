# SPDX-FileCopyrightText: 2026 Jordan Henshaw
#
# SPDX-License-Identifier: GPL-3.0-or-later

'''This is basically bpy_rna.cc, just way, wayyyyyy simpler.'''

test_subjects = {}

TYPE_REGISTRY = {
    "Hook": test_subjects,
}


def _register_class(cls):
    from . import types as blendfinals_types

    if not _validate_cls(cls)[0]:
        return

    for type_name, type_dict in TYPE_REGISTRY.items():
        base_class = getattr(blendfinals_types, type_name, None)

        if not is_corresponding_base(cls, base_class):
            continue

        allow_reregister(cls, type_dict)
        add_to_blendfinals_data(cls, type_dict)
        return
    
def is_corresponding_base(cls, base_class):
    return (base_class and issubclass(cls, base_class))
    
def allow_reregister(cls, type_dict):
    if cls.bf_idname in type_dict:
        del type_dict[cls.bf_idname]

def add_to_blendfinals_data(cls, type_dict):
    type_dict[cls.bf_idname] = cls


def _unregister_class(cls):
    bf_id = getattr(cls, 'bf_idname', None)
    for type_dict in TYPE_REGISTRY.values():
        if bf_id in type_dict:
            del type_dict[bf_id]
            return

    if bf_id != "alva_hook":
        print(f"\nWARNING: Class '{cls.__name__}' with ID '{bf_id}' was not found in registration.")


def _validate_cls(cls):
    from . import types as blendfinals_types

    required_attributes_map = {
        "Hook": {
            "bf_idname": "an 'bf_idname' attribute",
            "bf_label": "an 'bf_label' attribute",
            "start_test": "a 'start_test' method",
            "end_test": "an 'end_test' method",
        },
    }

    for type_name, requirements in required_attributes_map.items():
        base = getattr(blendfinals_types, type_name, None)
        if base and issubclass(cls, base):
            missing = []
            for attr, desc in requirements.items():
                if not hasattr(cls, attr):
                    missing.append(desc)
            if missing:
                print(f"\nERROR: Class '{cls.__name__}' is missing required attributes:")
                for issue in missing:
                    print(f"  - {issue}")
                return False, None
            return True, base

    print(f"Class {cls} does not have a valid mix-in class.")
    return False, None