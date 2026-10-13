/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */

/* Compact numeric formatting - no sprintf/printf (this codebase avoids
 * linking the printf core to save flash/RAM, see search_overlay.c). */
#ifndef CV4_FMT_H
#define CV4_FMT_H

#include <stdint.h>

/* Appends `value` in engineering notation (k/none/m/u prefix chosen so the
 * mantissa prints with <= 4 significant digits) followed by " " + unit to
 * dst (NUL-terminated, caller-sized buffer). Returns the new length.
 * fmt_eng(0, 6.667, "V") -> "6.667 V"; fmt_eng(0, 0.5, "ohm") -> "500 mohm";
 * fmt_eng(0, 21.333, "W") -> "21.33 W". unit may be "" for a bare number. */
uint8_t fmt_eng(char *dst, double value, const char *unit);

/* Plain fixed-point, up to 4 decimals, trailing zeros trimmed: 1.875 -> "1.875". */
uint8_t fmt_num(char *dst, double value);

/* Compact on-circuit label: engineering notation with NO spaces, prefix and
 * suffix concatenated onto the number. fmt_label(0,6000,"") -> "6k";
 * fmt_label(0,12,"V") -> "12V"; fmt_label(0,0.004,"A") -> "4mA". Used when a
 * component value has been edited (must fit inside the fixed-width symbol);
 * unedited values keep their original authored label verbatim. */
uint8_t fmt_label(char *dst, double value, const char *suffix);
uint8_t fmt_rect_label(char *dst, double re, double im);
uint8_t fmt_polar_label(char *dst, double re, double im, const char *suffix);

/* ---- phasor formatting -------------------------------------------------- */

/* Rectangular form: "3.2 + j4.1" / "3.2 - j4.1" / "3.2" when im == 0 /
 * "j4.1" when re == 0. Unit appended with a space when non-empty.
 * fmt_rect(0, 10.0, -5.0, "ohm") -> "10 - j5 ohm" */
uint8_t fmt_rect(char *dst, double re, double im, const char *unit);

/* Polar form, ASCII per the project convention: "5.2 /_51.3deg".
 * The angle is in DEGREES, normalised to (-180, 180].
 * fmt_polar(0, 0.5, -0.5, "A") -> "707.1 mA /_-45deg" */
uint8_t fmt_polar(char *dst, double re, double im, const char *unit);

/* Magnitude and angle of a phasor; `deg` in (-180, 180]. Exposed because
 * narrators need the numbers themselves, not just their text. */
double cx_mag(double re, double im);
double cx_deg(double re, double im);

#endif
