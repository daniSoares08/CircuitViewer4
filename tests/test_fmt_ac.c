/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */

/* Desktop-only test for the phasor formatting added in src/fmt.c.
 *   gcc -std=c99 -Wall -o tests/test_fmt_ac.exe tests/test_fmt_ac.c src/fmt.c -lm
 *   tests/test_fmt_ac.exe
 */
#include <stdio.h>
#include <string.h>
#include "../src/fmt.h"

static int failures = 0;

static void ck(const char *label, const char *got, const char *want) {
    if (strcmp(got, want) != 0) {
        printf("FAIL %-24s got=\"%s\" want=\"%s\"\n", label, got, want);
        failures++;
    } else {
        printf("ok   %-24s \"%s\"\n", label, got);
    }
}

int main(void) {
    char b[64];

    fmt_rect(b, 10.0, -5.0, "ohm");  ck("rect 10-j5",      b, "10 - j5 ohm");
    fmt_rect(b, 3.2, 4.1, "");       ck("rect 3.2+j4.1",   b, "3.2 + j4.1");
    fmt_rect(b, 7.0, 0.0, "V");      ck("rect real only",  b, "7 V");
    fmt_rect(b, 0.0, -2.5, "A");     ck("rect imag only",  b, "-j2.5 A");
    fmt_rect(b, 0.0, 0.0, "V");      ck("rect zero",       b, "0 V");
    fmt_eng(b, 10e-9, "F"); ck("nanofarads", b, "10 nF");
    fmt_eng(b, 200e-12, "F"); ck("picofarads", b, "200 pF");
    fmt_eng(b, 1.2e6, "VA"); ck("megavoltamp", b, "1.2 MVA");
    fmt_rect_label(b,2000,4000); ck("compact Z",b,"2k+j4k");
    fmt_rect_label(b,0,-4000); ck("compact -jX",b,"-j4k");
    fmt_polar_label(b,17.320508,10,"V"); ck("compact source",b,"20V/_30");

    fmt_polar(b, 0.5, -0.5, "A");    ck("polar -45",       b, "707.1 mA /_-45 deg");
    fmt_polar(b, 20.0, 0.0, "V");    ck("polar real",      b, "20 V /_0 deg");
    /* 17.32 + j10 = 20 /_30 - the canonical textbook phasor */
    fmt_polar(b, 17.320508, 10.0, "V"); ck("polar 30",     b, "20 V /_30 deg");

    if (failures) {
        printf("\n%d FAILURE(S)\n", failures);
        return 1;
    }
    printf("\nALL OK\n");
    return 0;
}
