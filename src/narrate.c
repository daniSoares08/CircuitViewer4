#include "narrate.h"

const char *unit_for_kind(uint8_t kind) {
    switch (kind) {
    case CK_RES: case CK_Z: return "ohm";
    case CK_VSRC: return "V";
    case CK_ISRC: return "A";
    case CK_DVS: case CK_DIS: return "";
    case CK_CAP: return "F";
    case CK_IND: return "H";
    default: return "";
    }
}
