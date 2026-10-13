/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */
#include <stdio.h>
#include <string.h>
#include "../src/fmt.h"

static int failures = 0;

static void check(double v, const char *unit, const char *want) {
    char buf[24];
    fmt_eng(buf, v, unit);
    if (strcmp(buf, want) != 0) {
        printf("FAIL fmt_eng(%g,\"%s\") = \"%s\" want \"%s\"\n", v, unit, buf, want);
        failures++;
    } else {
        printf("ok   fmt_eng(%g,\"%s\") = \"%s\"\n", v, unit, buf);
    }
}

int main(void) {
    check(12.0, "V", "12 V");
    check(6.667, "V", "6.667 V");
    check(0.5, "ohm", "500 mohm");
    check(21.333, "W", "21.33 W");
    check(0.6667, "A", "666.7 mA");
    check(13.4545, "V", "13.45 V");
    check(1.3333, "ohm", "1.333 ohm");
    check(6000.0, "ohm", "6 kohm");
    check(-24.0, "V", "-24 V");
    check(0.0, "V", "0 V");
    check(10.0, "ohm", "10 ohm");
    check(602.3, "W", "602.3 W");
    if (failures) { printf("\n%d FAILURE(S)\n", failures); return 1; }
    printf("\nALL OK\n");
    return 0;
}
