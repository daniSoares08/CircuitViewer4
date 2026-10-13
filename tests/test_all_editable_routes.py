#!/usr/bin/env python3
"""Shared ABI and end-to-end entry point: execute, never just count edits."""
import ctypes

class EditComp(ctypes.Structure):
    _fields_ = [
        ("kind", ctypes.c_uint8), ("na", ctypes.c_uint8),
        ("nb", ctypes.c_uint8), ("ctrl", ctypes.c_uint8),
        ("ctrl_a", ctypes.c_uint8), ("ctrl_b", ctypes.c_uint8),
        ("flags", ctypes.c_uint8), ("reg", ctypes.c_uint8),
        ("value", ctypes.c_float), ("deflt", ctypes.c_float),
        ("value_im", ctypes.c_float), ("deflt_im", ctypes.c_float),
    ]

def component_array(template):
    result = (EditComp * len(template["comps"]))()
    for index, src in enumerate(template["comps"]):
        result[index] = EditComp(
            src["kind"], src["na"], src["nb"], src.get("ctrl", 255),
            src.get("ctrl_a", 0), src.get("ctrl_b", 0),
            src.get("flags", 0), index, src["deflt"], src["deflt"],
            src.get("deflt_im", 0), src.get("deflt_im", 0))
    return result

def main():
    # Import after the ABI is defined; these modules also import it.
    import test_live_recipes
    import test_appvar_live
    test_live_recipes.main()
    test_appvar_live.main()

if __name__ == "__main__":
    main()
