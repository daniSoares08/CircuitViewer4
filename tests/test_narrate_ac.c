/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */

/* Desktop-only test for src/narrate_ac.c.
 *   gcc -std=c99 -Wall -o tests/test_narrate_ac.exe tests/test_narrate_ac.c \
 *       src/narrate_ac.c src/narrate.c src/engine.c src/mna.c src/fmt.c -lm
 *   tests/test_narrate_ac.exe
 *
 * Every expected value is derived in the comment above its test, so a
 * failure points at the code and not at a remembered number.
 */
#include <stdio.h>
#include <string.h>
#include "../src/narrate_ac.h"

static int failures = 0;

static void dump(const Narration *n) {
    uint8_t i;
    for (i = 0; i < n->count; i++) printf("      | %s\n", n->steps[i].text);
}

/* passes if some narrated line contains `needle` */
static void expect_line(const char *label, const Narration *n, const char *needle) {
    uint8_t i;
    for (i = 0; i < n->count; i++) {
        if (strstr(n->steps[i].text, needle)) {
            printf("ok   %-34s (found \"%s\")\n", label, needle);
            return;
        }
    }
    printf("FAIL %-34s missing \"%s\"\n", label, needle);
    dump(n);
    failures++;
}

static EditComp mk(uint8_t kind, uint8_t na, uint8_t nb, float v, float v_im) {
    EditComp c;
    memset(&c, 0, sizeof c);
    c.kind = kind;
    c.na = na;
    c.nb = nb;
    c.ctrl = 0xFF;
    c.value = v;
    c.deflt = v;
    c.value_im = v_im;
    c.deflt_im = v_im;
    return c;
}

/* Series RL across 10/_0 V: R = 10 ohm, L = 10 mH, w = 1000 rad/s.
 *   Z(L) = j10 ohm ; Z total = 10 + j10
 *   I = 10/(10+j10) = 0.5 - j0.5 => 707.1 mA /_-45 deg
 *   V(node2, across L) = I * j10 = 5 + j5 => 7.071 V /_45 deg          */
static void test_ac_nodal_rl(void) {
    EditComp comps[3];
    Narration nar;

    comps[0] = mk(CK_VSRC, 1, 0, 10.0f, 0.0f);
    comps[1] = mk(CK_RES,  1, 2, 10.0f, 0.0f);
    comps[2] = mk(CK_IND,  2, 0, 0.01f, 0.0f);

    if (!narrate_ac_nodal(comps, 3, 3, 1000.0, NULL, 0xFF, false, &nar)) {
        printf("FAIL ac_nodal_rl returned false (%s)\n", nar.impossible_reason);
        failures++;
        return;
    }
    /* fmt_eng puts 1000 rad/s in engineering notation, so this reads
       "1 krad/s" - the project's formatting convention, not a bug. */
    expect_line("RL: frequency stated", &nar, "w = 1 krad/s");
    expect_line("RL: Z(L) = j10 ohm",   &nar, "j10 ohm");
    expect_line("RL: V2 polar",         &nar, "7.071 V /_45 deg");
    expect_line("RL: V2 rectangular",   &nar, "5 + j5 V");
    expect_line("RL: V1 is the source", &nar, "10 V /_0 deg");
}

/* Series RC across 10/_0 V: R = 1 kohm, C = 1 uF, w = 1000 rad/s.
 *   Z(C) = -j1000 ohm
 *   V across C = 10 * (-j1000)/(1000 - j1000) = 5 - j5 => 7.071 /_-45  */
static void test_ac_nodal_rc(void) {
    EditComp comps[3];
    Narration nar;

    comps[0] = mk(CK_VSRC, 1, 0, 10.0f, 0.0f);
    comps[1] = mk(CK_RES,  1, 2, 1000.0f, 0.0f);
    comps[2] = mk(CK_CAP,  2, 0, 1e-6f, 0.0f);

    if (!narrate_ac_nodal(comps, 3, 3, 1000.0, NULL, 0xFF, false, &nar)) {
        printf("FAIL ac_nodal_rc returned false (%s)\n", nar.impossible_reason);
        failures++;
        return;
    }
    expect_line("RC: Z(C) = -j1000 ohm", &nar, "-j1 kohm");
    expect_line("RC: V2 polar",          &nar, "7.071 V /_-45 deg");
}

/* A source with a nonzero phase must carry its angle through untouched:
 * 20/_30 V (= 17.3205 + j10) across a lone 4 ohm resistor. */
static void test_ac_source_phase(void) {
    EditComp comps[2];
    Narration nar;

    comps[0] = mk(CK_VSRC, 1, 0, 17.320508f, 10.0f);
    comps[1] = mk(CK_RES,  1, 0, 4.0f, 0.0f);

    if (!narrate_ac_nodal(comps, 2, 2, 377.0, NULL, 0xFF, false, &nar)) {
        printf("FAIL ac_source_phase returned false (%s)\n", nar.impossible_reason);
        failures++;
        return;
    }
    expect_line("phase: V1 keeps 30 deg", &nar, "20 V /_30 deg");
}

/* Series R + L between the two ports: Zeq must be 10 + j10 at w=1000.
 * Also checks Y = 1/Z = 0.05 - j0.05 S. */
static void test_ac_impedance_series(void) {
    EditComp comps[2];
    Narration nar;

    comps[0] = mk(CK_RES, 1, 2, 10.0f, 0.0f);
    comps[1] = mk(CK_IND, 2, 0, 0.01f, 0.0f);

    if (!narrate_ac_impedance(comps, 2, 3, 1000.0, 1, 0, &nar)) {
        printf("FAIL ac_impedance returned false (%s)\n", nar.impossible_reason);
        failures++;
        return;
    }
    expect_line("Zeq rectangular",  &nar, "10 + j10 ohm");
    expect_line("Zeq polar",        &nar, "14.14 ohm /_45 deg");
    expect_line("Yeq",              &nar, "50 - j50 mS");
}

/* Parallel LC at resonance: the reactive parts cancel and Zeq collapses to
 * the resistor alone. w0 = 1/sqrt(LC) with L=1mH, C=1uF -> 31622.78 rad/s. */
static void test_ac_impedance_resonance(void) {
    EditComp comps[3];
    Narration nar;

    comps[0] = mk(CK_RES, 1, 0, 50.0f, 0.0f);
    comps[1] = mk(CK_IND, 1, 0, 0.001f, 0.0f);
    comps[2] = mk(CK_CAP, 1, 0, 1e-6f, 0.0f);

    if (!narrate_ac_impedance(comps, 3, 2, 31622.7766, 1, 0, &nar)) {
        printf("FAIL ac_resonance returned false (%s)\n", nar.impossible_reason);
        failures++;
        return;
    }
    expect_line("resonance: Zeq is purely real", &nar, "50 ohm");
}

static void test_remaining_ac_narrators(void) {
    EditComp c[4];
    Narration nar;

    /* One 10 V source and 5 ohm resistor: mesh current = 2 A. */
    {
        MeshEdge edges[] = {{1, 1}, {0, 1}};
        const MeshEdge *meshes[] = {edges};
        uint8_t lens[] = {2};
        c[0] = mk(CK_VSRC, 1, 0, 10, 0);
        c[1] = mk(CK_Z, 1, 0, 5, 0);
        if (!narrate_ac_mesh(c, 2, 2, 1.0, meshes, lens, 1, 0xFF, &nar)) {
            printf("FAIL AC mesh returned false\n"); failures++;
        } else expect_line("AC mesh current", &nar, "2 A /_0 deg");
    }

    /* Two current sources inject 1 A and 2 A into a 1 ohm branch. */
    c[0] = mk(CK_ISRC, 0, 1, 1, 0);
    c[1] = mk(CK_ISRC, 0, 1, 2, 0);
    c[2] = mk(CK_Z, 1, 0, 1, 0);
    if (!narrate_ac_superposition(c, 3, 2, 1.0, 2, &nar)) {
        printf("FAIL AC superposition returned false\n"); failures++;
    } else expect_line("AC superposition sum", &nar, "3 A /_0 deg");

    /* Open port after a 5 ohm series resistor: Vth=10 V, Zth=5 ohm. */
    c[0] = mk(CK_VSRC, 1, 0, 10, 0);
    c[1] = mk(CK_Z, 1, 2, 5, 0);
    if (!narrate_ac_thevenin(c, 2, 3, 1.0, 2, 0, &nar)) {
        printf("FAIL AC Thevenin returned false\n"); failures++;
    } else {
        expect_line("AC Thevenin voltage", &nar, "10 V /_0 deg");
        expect_line("AC Thevenin impedance", &nar, "5 ohm");
    }

    /* 10 Vrms on 5 ohm absorbs 20 W. */
    c[0] = mk(CK_VSRC, 1, 0, 10, 0);
    c[1] = mk(CK_Z, 1, 0, 5, 0);
    if (!narrate_ac_power(c, 2, 2, 1.0, 1, false, false, &nar)) {
        printf("FAIL AC power returned false\n"); failures++;
    } else expect_line("AC active power", &nar, "P = 20 W");
}

int main(void) {
    test_ac_nodal_rl();
    test_ac_nodal_rc();
    test_ac_source_phase();
    test_ac_impedance_series();
    test_ac_impedance_resonance();
    test_remaining_ac_narrators();
    if (failures) {
        printf("\n%d FAILURE(S)\n", failures);
        return 1;
    }
    printf("\nALL OK\n");
    return 0;
}
