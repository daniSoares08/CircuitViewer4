/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */
#ifndef CV4_NARRATE_H
#define CV4_NARRATE_H

#include "engine.h"

/* Colors, mirrored from cv3.h's COL_* so this stays a portable/testable
 * module (no tice.h/graphx.h dependency); engine glue maps these 1:1. */
enum { NCOL_BLACK = 1, NCOL_BLUE = 4, NCOL_RED = 5 };

const char *unit_for_kind(uint8_t kind);

#endif
