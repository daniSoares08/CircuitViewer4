/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */

/* Desktop-only regression test for src/mna.c against known textbook
 * answers (see EXERCISE_MANIFEST.md). Build+run with plain gcc, no CE
 * toolchain needed:
 *   gcc -std=c99 -Wall -o tests/test_mna.exe tests/test_mna.c src/mna.c -lm
 *   tests/test_mna.exe
 */
#include <stdio.h>
#include <math.h>
#include "../src/mna.h"

static int failures = 0;

static void check(const char *label, double got, double want, double tol) {
    if (fabs(got - want) > tol) {
        printf("FAIL %-28s got=%.4f want=%.4f\n", label, got, want);
        failures++;
    } else {
        printf("ok   %-28s got=%.4f want=%.4f\n", label, got, want);
    }
}

/* p1_q3 (Prova01 Q3): 12V and 20V sources, 10/10 parallel + 10 + 4 ohm.
 * Book/manifest answer: V1(=node2 here) = 13.45 V. */
static void test_p1_q3(void) {
    MnaTopology t = {0};
    MnaResult r;
    t.n_nodes = 4; /* 0=gnd,1,2,3 */
    t.n_elems = 6;
    t.elems[0] = (MnaElem){ EK_R, 1, 2, 0xFF, 0, 0, 10.0, 0.0 };
    t.elems[1] = (MnaElem){ EK_R, 1, 2, 0xFF, 0, 0, 10.0, 0.0 };
    t.elems[2] = (MnaElem){ EK_R, 2, 0, 0xFF, 0, 0, 10.0, 0.0 };
    t.elems[3] = (MnaElem){ EK_R, 2, 3, 0xFF, 0, 0, 4.0, 0.0 };
    t.elems[4] = (MnaElem){ EK_VSRC, 1, 0, 0xFF, 0, 0, 12.0, 0.0 };
    t.elems[5] = (MnaElem){ EK_VSRC, 3, 0, 0xFF, 0, 0, 20.0, 0.0 };
    if (!mna_solve(&t, &r)) { printf("FAIL p1_q3 solve returned false\n"); failures++; return; }
    check("p1_q3 V1(node1)", r.node_v[1], 12.0, 1e-6);
    check("p1_q3 V2(node2)", r.node_v[2], 13.4545, 1e-3);
    check("p1_q3 V3(node3)", r.node_v[3], 20.0, 1e-6);
}

/* rec_q4: 60V/24V sources, 12+12+6 ohm. Manifest/solution-text answer:
 * V0 = 3 V, derived from "(V0-60)/12 + V0/12 + (V0+24)/6 = 0" - the "+24"
 * (not "-24") proves the ORIGINAL exam figure has the 24V source's "-"
 * terminal on top (at node D) even though v3's draw_voltage_source() always
 * draws "+" on top (it has no polarity parameter) - a real v3 draw/math
 * mismatch that v4's polarity flag is designed to fix. Topology (from
 * CIRCUITS['rec_q4']): vsrc_v 60V A(top,+)-gnd; res_h 12 A-C; res_v 12
 * C-gnd; res_h 6 C-D; vsrc_v 24V gnd(+)-D(-) i.e. na=0,nb=D here. */
static void test_rec_q4(void) {
    MnaTopology t = {0};
    MnaResult r;
    t.n_nodes = 4;
    t.n_elems = 5;
    t.elems[0] = (MnaElem){ EK_VSRC, 1, 0, 0xFF, 0, 0, 60.0, 0.0 };
    t.elems[1] = (MnaElem){ EK_R, 1, 2, 0xFF, 0, 0, 12.0, 0.0 };
    t.elems[2] = (MnaElem){ EK_R, 2, 0, 0xFF, 0, 0, 12.0, 0.0 };
    t.elems[3] = (MnaElem){ EK_R, 2, 3, 0xFF, 0, 0, 6.0, 0.0 };
    t.elems[4] = (MnaElem){ EK_VSRC, 0, 3, 0xFF, 0, 0, 24.0, 0.0 };
    if (!mna_solve(&t, &r)) { printf("FAIL rec_q4 solve returned false\n"); failures++; return; }
    check("rec_q4 V0(node2)", r.node_v[2], 3.0, 1e-3);
    check("rec_q4 V_D(node3)", r.node_v[3], -24.0, 1e-6);
}

/* p1_q1: 20A current source into a resistor ladder, Req=1.33 ohm as seen by
 * the source, so V across the source (node1 wrt gnd) = 20*1.333 = 26.67 V.
 * Ladder (from CIRCUITS['p1_q1']): isrc 20A between gnd(bottom rail) and
 * node1(top-left); 2 ohm node1-node2; 1 ohm node2-node3; 3 ohm node3-gnd
 * (vertical); 4 ohm node3-node4; 6 ohm node4-gnd; 8 ohm node4-node5;
 * 12 ohm node5-gnd; 1.2 ohm node3-node4(bottom rung, parallel path) --
 * simplified here to just the top ladder since this test only exists to
 * sanity-check current-source sign convention, not to re-derive the whole
 * figure; use the textbook Req instead: single 20A source across a 1.333
 * ohm net -> V=26.667 V. */
static void test_isrc_sign(void) {
    MnaTopology t = {0};
    MnaResult r;
    t.n_nodes = 2;
    t.n_elems = 2;
    t.elems[0] = (MnaElem){ EK_ISRC, 0, 1, 0xFF, 0, 0, 20.0, 0.0 }; /* injects into node1 */
    t.elems[1] = (MnaElem){ EK_R, 1, 0, 0xFF, 0, 0, 1.3333333, 0.0 };
    if (!mna_solve(&t, &r)) { printf("FAIL isrc_sign solve returned false\n"); failures++; return; }
    check("isrc_sign V1", r.node_v[1], 26.667, 1e-2);
}

/* p1_q5 (Prova01 Q5): superposition over the same topology auto-derived
 * from CIRCUITS['p1_q5'] (union-find on op coordinates). NOTE: v3's
 * solution text claims i1=2.5A/i2=0.375A/i3=-1A (sum 1.875A), but hand
 * re-derivation via current-divider on the ACTUAL drawn topology (2A
 * source in parallel with the 3-ohm resistor between nodes B/C, B tied to
 * gnd via 1||2=0.667 ohm, C tied to gnd via 5||4=2.222 ohm) independently
 * gives i(2A alone) = 2*2.889/5.889 = 0.9811 A, matching this solver
 * exactly - i.e. the OLD v3 text for this one looks wrong, not this
 * engine (memory: "codex .md/manifest answers contain ERRORS, re-derive").
 * Flagged for the real content migration; this test only pins the solver's
 * internal linearity (contributions must sum to the full-circuit answer),
 * which is what actually matters for a regression test. */
static void test_p1_q5_superposition(void) {
    MnaTopology t = {0};
    MnaResult r;
    double i1, i2, i3, itot;

    t.n_nodes = 5; /* 0=gnd,1=A,2=B,3=C,4=D */
    t.n_elems = 8;
    t.elems[0] = (MnaElem){ EK_VSRC, 1, 0, 0xFF, 0, 0, 20.0, 0.0 };
    t.elems[1] = (MnaElem){ EK_R,    1, 2, 0xFF, 0, 0, 2.0, 0.0 };
    t.elems[2] = (MnaElem){ EK_R,    2, 0, 0xFF, 0, 0, 1.0, 0.0 };
    t.elems[3] = (MnaElem){ EK_ISRC, 3, 2, 0xFF, 0, 0, 2.0, 0.0 };
    t.elems[4] = (MnaElem){ EK_R,    2, 3, 0xFF, 0, 0, 3.0, 0.0 }; /* "i" = B->C */
    t.elems[5] = (MnaElem){ EK_R,    3, 0, 0xFF, 0, 0, 4.0, 0.0 };
    t.elems[6] = (MnaElem){ EK_R,    3, 4, 0xFF, 0, 0, 5.0, 0.0 };
    t.elems[7] = (MnaElem){ EK_VSRC, 4, 0, 0xFF, 0, 0, 16.0, 0.0 };

    if (!mna_solve_only(&t, 0, &r)) { printf("FAIL p1_q5 sub(20V) solve\n"); failures++; return; }
    i1 = r.elem_i[4];
    if (!mna_solve_only(&t, 3, &r)) { printf("FAIL p1_q5 sub(2A) solve\n"); failures++; return; }
    i2 = r.elem_i[4];
    check("p1_q5 i2 (2A alone, hand-checked)", i2, 0.9811, 1e-3);
    if (!mna_solve_only(&t, 7, &r)) { printf("FAIL p1_q5 sub(16V) solve\n"); failures++; return; }
    i3 = r.elem_i[4];

    if (!mna_solve(&t, &r)) { printf("FAIL p1_q5 full solve\n"); failures++; return; }
    itot = r.elem_i[4];
    check("p1_q5 i1+i2+i3 == i total (linearity)", i1 + i2 + i3, itot, 1e-6);
}

/* ---- phasor (AC) tests --------------------------------------------------
 * Every expected value below is derived analytically in the comment, so a
 * failure points at the solver rather than at a remembered number. */

static void check_polar(const char *label, double re, double im,
                        double want_mag, double want_deg) {
    double mag = sqrt(re * re + im * im);
    double deg = atan2(im, re) * 180.0 / 3.14159265358979323846;
    check(label, mag, want_mag, 1e-3);
    /* only compare the angle when the magnitude is meaningful */
    if (want_mag > 1e-9) {
        char buf[64];
        snprintf(buf, sizeof buf, "%s (ang)", label);
        check(buf, deg, want_deg, 1e-2);
    }
}

/* Series RL fed by 10/_0 V: R = 10 ohm, L = 10 mH, w = 1000 rad/s.
 *   Z = 10 + j(1000 * 0.01) = 10 + j10
 *   I = 10 / (10 + j10) = 10(10 - j10)/200 = 0.5 - j0.5
 *     => |I| = 0.70711 A at -45 deg                                    */
static void test_ac_series_rl(void) {
    MnaTopology t = {0};
    MnaResult r;
    t.n_nodes = 3;   /* 0=gnd, 1=source top, 2=between R and L */
    t.n_elems = 3;
    t.omega = 1000.0;
    t.elems[0] = (MnaElem){ EK_VSRC, 1, 0, 0xFF, 0, 0, 10.0, 0.0 };
    t.elems[1] = (MnaElem){ EK_R,    1, 2, 0xFF, 0, 0, 10.0, 0.0 };
    t.elems[2] = (MnaElem){ EK_L,    2, 0, 0xFF, 0, 0, 0.01, 0.0 };

    if (!mna_solve(&t, &r)) { printf("FAIL ac_series_rl solve\n"); failures++; return; }
    /* the source's own current is -I by its na->nb reference direction */
    check_polar("AC RL current", -r.elem_i[0], -r.elem_i_im[0], 0.70711, -45.0);
    /* V across L = I * jwL = (0.5 - j0.5)(j10) = 5 + j5 => 7.0711 at +45 */
    check_polar("AC RL v(L)", r.node_v[2], r.node_v_im[2], 7.07107, 45.0);
}

/* Series RC fed by 10/_0 V: R = 1 kohm, C = 1 uF, w = 1000 rad/s.
 *   Zc = -j/(1000 * 1e-6) = -j1000
 *   Z  = 1000 - j1000
 *   I  = 10 / (1000 - j1000) = 10(1000 + j1000)/2e6 = 0.005 + j0.005
 *     => |I| = 7.0711 mA at +45 deg                                    */
static void test_ac_series_rc(void) {
    MnaTopology t = {0};
    MnaResult r;
    t.n_nodes = 3;
    t.n_elems = 3;
    t.omega = 1000.0;
    t.elems[0] = (MnaElem){ EK_VSRC, 1, 0, 0xFF, 0, 0, 10.0, 0.0 };
    t.elems[1] = (MnaElem){ EK_R,    1, 2, 0xFF, 0, 0, 1000.0, 0.0 };
    t.elems[2] = (MnaElem){ EK_C,    2, 0, 0xFF, 0, 0, 1e-6, 0.0 };

    if (!mna_solve(&t, &r)) { printf("FAIL ac_series_rc solve\n"); failures++; return; }
    check_polar("AC RC current", -r.elem_i[0], -r.elem_i_im[0], 0.0070711, 45.0);
}

/* Parallel LC at resonance driven by a 1/_0 A source, with R = 50 ohm.
 *   w0 = 1/sqrt(LC); at w0 the L and C admittances cancel exactly, so the
 *   source sees R alone and V = I*R = 50 /_0 V. This is the sharpest test
 *   of the imaginary block: any sign error breaks the cancellation.     */
static void test_ac_resonance(void) {
    MnaTopology t = {0};
    MnaResult r;
    double L = 0.001, C = 1e-6;
    t.n_nodes = 2;
    t.n_elems = 4;
    t.omega = 1.0 / sqrt(L * C);    /* = 31622.7766 rad/s */
    t.elems[0] = (MnaElem){ EK_ISRC, 0, 1, 0xFF, 0, 0, 1.0, 0.0 };
    t.elems[1] = (MnaElem){ EK_R,    1, 0, 0xFF, 0, 0, 50.0, 0.0 };
    t.elems[2] = (MnaElem){ EK_L,    1, 0, 0xFF, 0, 0, L,    0.0 };
    t.elems[3] = (MnaElem){ EK_C,    1, 0, 0xFF, 0, 0, C,    0.0 };

    if (!mna_solve(&t, &r)) { printf("FAIL ac_resonance solve\n"); failures++; return; }
    check_polar("AC resonance V", r.node_v[1], r.node_v_im[1], 50.0, 0.0);
}

/* A phasor SOURCE with a nonzero angle, feeding a pure resistor: the node
 * voltage must come back with the same angle it went in with. Catches an
 * RHS that only carries the real part. 20/_30 V across 4 ohm. */
static void test_ac_source_angle(void) {
    MnaTopology t = {0};
    MnaResult r;
    /* 20/_30 = 20cos30 + j20sin30 = 17.32051 + j10 */
    t.n_nodes = 2;
    t.n_elems = 2;
    t.omega = 377.0;
    t.elems[0] = (MnaElem){ EK_VSRC, 1, 0, 0xFF, 0, 0, 17.320508, 10.0 };
    t.elems[1] = (MnaElem){ EK_R,    1, 0, 0xFF, 0, 0, 4.0, 0.0 };

    if (!mna_solve(&t, &r)) { printf("FAIL ac_source_angle solve\n"); failures++; return; }
    check_polar("AC source angle V", r.node_v[1], r.node_v_im[1], 20.0, 30.0);
    /* I = V/R = 5/_30 A */
    check_polar("AC source angle I", r.elem_i[1], r.elem_i_im[1], 5.0, 30.0);
}

/* omega == 0 must still take the original real path and give the original
 * answer. This is the guard that the AC work did not disturb DC. */
static void test_dc_path_untouched(void) {
    MnaTopology t = {0};
    MnaResult r;
    t.n_nodes = 3;
    t.n_elems = 3;
    t.omega = 0.0;
    t.elems[0] = (MnaElem){ EK_VSRC, 1, 0, 0xFF, 0, 0, 10.0, 0.0 };
    t.elems[1] = (MnaElem){ EK_R,    1, 2, 0xFF, 0, 0, 10.0, 0.0 };
    t.elems[2] = (MnaElem){ EK_R,    2, 0, 0xFF, 0, 0, 10.0, 0.0 };
    if (!mna_solve(&t, &r)) { printf("FAIL dc_path solve\n"); failures++; return; }
    check("DC divider node2", r.node_v[2], 5.0, 1e-9);
    check("DC leaves imag zero", r.node_v_im[2], 0.0, 0.0);
}

static void test_ideal_opamp(void) {
    int ac;
    for(ac=0;ac<2;ac++) {
        MnaTopology t={0};MnaResult r;
        t.n_nodes=4;t.n_elems=5;t.omega=ac?1000:0;
        t.elems[0]=(MnaElem){EK_VSRC,1,0,255,0,0,2,ac?1:0};
        t.elems[1]=(MnaElem){EK_R,3,2,255,0,0,20000,0};
        t.elems[2]=(MnaElem){EK_R,2,0,255,0,0,10000,0};
        t.elems[3]=(MnaElem){EK_R,3,0,255,0,0,1000,0};
        t.elems[4]=(MnaElem){EK_OPAMP,3,0,255,1,2,0,0};
        if(!mna_solve(&t,&r)) { puts("FAIL ideal noninverter solve");failures++;continue; }
        check("AOP noninverter real",r.node_v[3],6,1e-5);
        check("AOP noninverter imag",r.node_v_im[3],ac?3:0,1e-5);
        check("AOP no input current",r.elem_i[0],0,1e-5);
        t.elems[2].na=1;t.elems[2].nb=2;t.elems[4].ctrl_a=0;
        if(!mna_solve(&t,&r)) { puts("FAIL ideal inverter solve");failures++;continue; }
        check("AOP inverter real",r.node_v[3],-4,1e-5);
        check("AOP inverter imag",r.node_v_im[3],ac?-2:0,1e-5);
    }
}
int main(void) {
    test_ideal_opamp();
    test_p1_q3();
    test_rec_q4();
    test_isrc_sign();
    test_p1_q5_superposition();
    test_dc_path_untouched();
    test_ac_series_rl();
    test_ac_series_rc();
    test_ac_resonance();
    test_ac_source_angle();
    if (failures) {
        printf("\n%d FAILURE(S)\n", failures);
        return 1;
    }
    printf("\nALL OK\n");
    return 0;
}
