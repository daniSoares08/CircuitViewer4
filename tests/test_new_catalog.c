#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../src/narrate_ac.h"
#include "../src/narrate_power.h"
#include "../src/fmt.h"

static int failures;

static EditComp comp(uint8_t kind, uint8_t na, uint8_t nb, float re, float im) {
    EditComp c;
    memset(&c, 0, sizeof c);
    c.kind = kind; c.na = na; c.nb = nb; c.ctrl = 0xFF;
    c.value = c.deflt = re; c.value_im = c.deflt_im = im;
    return c;
}

static EditComp polar_comp(uint8_t kind, uint8_t na, uint8_t nb,
                           double mag, double deg) {
    double rad = deg * 3.14159265358979323846 / 180.0;
    return comp(kind, na, nb, (float)(mag * cos(rad)),
                (float)(mag * sin(rad)));
}

static void near(const char *name, double got, double want, double tol) {
    if (fabs(got - want) > tol) {
        printf("FAIL %s: got %.6f want %.6f\n", name, got, want); failures++;
    } else printf("ok   %s\n", name);
}

static int contains(const Narration *n, const char *text) {
    uint8_t i;
    for (i = 0; i < n->count; i++) if (strstr(n->steps[i].text, text)) return 1;
    return 0;
}

static void complete(const char *name, const Narration *n,
                     const char *step, const char *result) {
    if (n->count > NARRATE_MAXLINES || !contains(n, step) || !contains(n, result)) {
        printf("FAIL %s incomplete/truncated (%u lines)\n", name, n->count);
        failures++;
    } else printf("ok   %s complete (%u lines)\n", name, n->count);
}

static void dump_if_requested(const char *title, const Narration *n) {
    uint8_t i;
    if (!getenv("CV4_DUMP")) return;
    printf("\n[%s]\n", title);
    for (i = 0; i < n->count; i++) printf("%s\n", n->steps[i].text);
}

static void chapter9(void) {
    EditComp c[3]; MnaTopology t; MnaResult r; Narration narration; uint8_t map[COMP_MAXN];
    double zr, zi, den;
    c[0] = comp(CK_Z, 1, 0, 4, 0);
    c[1] = comp(CK_Z, 1, 0, 0, 8);
    c[2] = comp(CK_Z, 1, 0, 0, -10);
    t.n_nodes = 2; build_mna_ac(c, 3, 1.0, &t, map);
    if (!mna_solve_test_source(&t, 1, 0, &r)) { puts("FAIL cap9 solve"); failures++; return; }
    zr = r.node_v[1]; zi = r.node_v_im[1]; den = zr*zr + zi*zi;
    near("cap9 Y real", zr/den, 0.250, 1e-5);
    near("cap9 Y imag", -zi/den, -0.025, 1e-5);
    narrate_ac_impedance(c, 3, 2, 1.0, 1, 0, &narration);
    dump_if_requested("Capitulo 9", &narration);
    if (!contains(&narration, "Yeq = Y1 + Y2 + Y3") ||
        !contains(&narration, "250 - j25 mS")) {
        puts("FAIL cap9 direct admittance steps"); failures++;
    } else puts("ok   cap9 direct admittance steps");
    complete("cap9 narration", &narration, "Zeq = 1/Yeq",
             "Y = 251.2 mS /_-5.711 deg");
}

static void selected_chapter9(void) {
    EditComp c[6]; MnaTopology t; MnaResult r; uint8_t map[COMP_MAXN];
    double mag, deg;

    c[0] = comp(CK_VSRC, 1, 0, 50, 0);
    c[1] = comp(CK_RES, 1, 2, 10, 0);
    c[2] = comp(CK_CAP, 2, 3, 0.005f, 0);
    c[3] = comp(CK_IND, 3, 0, 0.02f, 0);
    t.n_nodes = 4; build_mna_ac(c, 4, 200.0, &t, map); mna_solve(&t, &r);
    mag = cx_mag(r.elem_i[map[1]], r.elem_i_im[map[1]]);
    deg = cx_deg(r.elem_i[map[1]], r.elem_i_im[map[1]]);
    near("p9.35 |i|", mag, 4.789, 0.002); near("p9.35 angle", deg, -16.70, 0.02);

    c[0] = comp(CK_VSRC, 1, 0, 60, 0);
    c[1] = comp(CK_RES, 1, 2, 50, 0);
    c[2] = comp(CK_Z, 2, 0, 0, 80);
    c[3] = comp(CK_RES, 2, 3, 100, 0);
    c[4] = comp(CK_Z, 3, 0, 0, -40);
    t.n_nodes = 4; build_mna_ac(c, 5, 1.0, &t, map); mna_solve(&t, &r);
    mag = cx_mag(r.elem_i[map[1]], r.elem_i_im[map[1]]);
    deg = cx_deg(r.elem_i[map[1]], r.elem_i_im[map[1]]);
    near("p9.43 |Io|", mag, 0.4997, 0.0002); near("p9.43 angle", deg, -28.85, 0.02);

    c[0] = comp(CK_VSRC, 1, 0, 6, 0);
    c[1] = comp(CK_RES, 1, 2, 5, 0);
    c[2] = comp(CK_RES, 2, 0, 4, 0);
    c[3] = comp(CK_IND, 2, 0, 0.01f, 0);
    c[4] = comp(CK_CAP, 2, 3, 0.005f, 0);
    c[5] = comp(CK_RES, 3, 0, 3, 0);
    t.n_nodes = 4; build_mna_ac(c, 6, 200.0, &t, map); mna_solve(&t, &r);
    mag = cx_mag(r.elem_i[map[1]], r.elem_i_im[map[1]]);
    deg = cx_deg(r.elem_i[map[1]], r.elem_i_im[map[1]]);
    near("p9.44 |i|", mag, 0.96010, 0.0002); near("p9.44 angle", deg, -7.9549, 0.02);

    c[0] = comp(CK_RES, 1, 2, 12, 0);
    c[1] = comp(CK_CAP, 2, 3, 50e-6f, 0);
    c[2] = comp(CK_IND, 3, 0, 0.06f, 0);
    c[3] = comp(CK_RES, 3, 0, 40, 0);
    t.n_nodes = 4; build_mna_ac(c, 4, 377.0, &t, map);
    if (!mna_solve_test_source(&t, 1, 0, &r)) { puts("FAIL p9.56 solve"); failures++; }
    else {
        mag = cx_mag(r.node_v[1], r.node_v_im[1]);
        deg = cx_deg(r.node_v[1], r.node_v_im[1]);
        near("p9.56 |Zeq|", mag, 41.9544, 0.002);
        near("p9.56 angle", deg, -58.866, 0.02);
    }
}

static void chapter10(void) {
    EditComp c[6]; MnaTopology t; MnaResult r; Narration narration; uint8_t map[COMP_MAXN];
    double rad = 20.0 * 3.14159265358979323846 / 180.0;
    double mag, deg;
    c[0] = comp(CK_VSRC, 1, 0, (float)(100*cos(rad)), (float)(100*sin(rad)));
    c[1] = comp(CK_Z, 1, 2, 0, 4);
    c[2] = comp(CK_Z, 2, 0, 3, 0);
    c[3] = comp(CK_Z, 1, 3, 1, 0);
    c[4] = comp(CK_Z, 3, 0, 0, -2);
    c[5] = comp(CK_Z, 2, 3, 2, 0);
    t.n_nodes = 4; build_mna_ac(c, 6, 1.0, &t, map);
    if (!mna_solve(&t, &r)) { puts("FAIL cap10 solve"); failures++; return; }
    mag = cx_mag(r.elem_i[map[5]], r.elem_i_im[map[5]]);
    deg = cx_deg(r.elem_i[map[5]], r.elem_i_im[map[5]]);
    near("cap10 Io magnitude", mag, 9.25, 0.02);
    near("cap10 Io angle", deg, -162.12, 0.05);
    narrate_ac_nodal(c, 6, 4, 1.0, NULL, 5, false, &narration);
    dump_if_requested("Capitulo 10", &narration);
    if (!contains(&narration, "Io = 9.253 A /_-162.1 deg")) {
        puts("FAIL cap10 narrated target"); failures++;
    } else puts("ok   cap10 narrated target");
    complete("cap10 narration", &narration, "KCL no no V2",
             "Io = 9.253 A /_-162.1 deg");
}

/* Values copied from the three selected chapter-10 problems.  These checks
 * complement the generic narrator test above: they catch an incorrect node,
 * source direction or target mapping in the new catalog. */
static void selected_chapter10(void) {
    EditComp c[6]; MnaTopology t; MnaResult r; uint8_t map[COMP_MAXN];
    double mag, deg;

    c[0] = comp(CK_VSRC, 1, 0, 2, 0);
    c[1] = comp(CK_RES, 1, 2, 1, 0);
    c[2] = comp(CK_CAP, 2, 0, 1, 0);
    c[3] = comp(CK_IND, 2, 0, 1, 0);
    c[4] = comp(CK_RES, 2, 0, 1, 0);
    t.n_nodes = 3; build_mna_ac(c, 5, 10.0, &t, map);
    if (!mna_solve(&t, &r)) { puts("FAIL p10.1 solve"); failures++; }
    else {
        mag = cx_mag(r.elem_i[map[1]], r.elem_i_im[map[1]]);
        deg = cx_deg(r.elem_i[map[1]], r.elem_i_im[map[1]]);
        near("p10.1 |i|", mag, 1.9704, 0.001);
        near("p10.1 angle", deg, 5.6533, 0.01);
    }

    c[0] = polar_comp(CK_VSRC, 1, 0, 120, -15);
    c[1] = comp(CK_RES, 1, 2, 40, 0);
    c[2] = comp(CK_Z, 2, 3, 0, 20);
    c[3] = polar_comp(CK_ISRC, 3, 0, 6, 30);
    c[4] = comp(CK_Z, 3, 0, 0, -30);
    c[5] = comp(CK_RES, 3, 0, 50, 0);
    t.n_nodes = 4; build_mna_ac(c, 6, 1.0, &t, map);
    if (!mna_solve(&t, &r)) { puts("FAIL p10.7 solve"); failures++; }
    else {
        mag = cx_mag(r.node_v[3], r.node_v_im[3]);
        deg = cx_deg(r.node_v[3], r.node_v_im[3]);
        near("p10.7 |V|", mag, 124.08, 0.02);
        near("p10.7 angle", deg, -154.0, 0.05);
    }

    c[0] = comp(CK_VSRC, 1, 0, 10, 0);
    c[1] = comp(CK_RES, 1, 2, 2000, 0);
    c[2] = comp(CK_IND, 2, 0, 0.4f, 0);
    c[3] = comp(CK_CAP, 2, 3, 1e-6f, 0);
    c[4] = polar_comp(CK_VSRC, 3, 0, 20, -90);
    t.n_nodes = 4; build_mna_ac(c, 5, 1000.0, &t, map);
    if (!mna_solve(&t, &r)) { puts("FAIL p10.26 solve"); failures++; }
    else {
        mag = cx_mag(r.elem_i[map[2]], r.elem_i_im[map[2]]);
        deg = cx_deg(r.elem_i[map[2]], r.elem_i_im[map[2]]);
        near("p10.26 |io|", mag, 0.039528, 0.0001);
        near("p10.26 angle", deg, -18.435, 0.05);
    }
}

static void selected_chapters11_12(void) {
    EditComp c[5]; Narration n;
    float p11_1[] = {1670, 0, 33, 60, 50};
    float p11_53[] = {4000, 0.8f, -1, 2400, 0.6f, 1, 1000, 500, 120, 30};
    float p11_69[] = {120, 60, 10, 12};
    float p12_7[] = {440, 0, 0, 0, 6, -8};
    float p12_14[] = {100, 0, 1, 2, 12, 12};
    float p12_25[] = {440, 10, 3, 2, 10, -8};

    narrate_power_profile(4, p11_1, 5, &n);
    dump_if_requested("Problema 11.1", &n);
    complete("p11.1 narration", &n, "Produto seno-cosseno", "Pmed = 13.78 kW");

    c[0] = comp(CK_ISRC, 0, 1, 6, 0);
    c[1] = comp(CK_Z, 1, 0, 0, 10);
    c[2] = comp(CK_Z, 1, 2, 0, -20);
    c[3] = comp(CK_DIS, 0, 2, 0.5f, 0); c[3].ctrl = 2;
    c[4] = comp(CK_RES, 2, 0, 40, 0);
    narrate_ac_power(c, 5, 3, 1.0, 4, true, false, &n);
    dump_if_requested("Problema 11.8", &n);
    complete("p11.8 narration", &n, "Fasores de pico", "P = 43.78 W");
    if (!contains(&n, "FP = 1 unitario")) {
        puts("FAIL p11.8 power-factor sense"); failures++;
    } else puts("ok   p11.8 power-factor sense");

    c[0] = comp(CK_VSRC, 1, 0, 12, 0);
    c[1] = comp(CK_RES, 1, 2, 1, 0);
    c[2] = comp(CK_Z, 2, 0, 0, 1);
    c[3] = comp(CK_Z, 2, 3, 0, -1);
    c[4] = comp(CK_DIS, 0, 3, 2, 0); c[4].ctrl_a = 2; c[4].ctrl_b = 0;
    narrate_ac_max_power(c, 5, 4, 1.0, 3, 0, true, &n);
    dump_if_requested("Problema 11.15", &n);
    complete("p11.15 narration", &n, "Casamento conjugado", "Pmax = 90 W");
    if (!contains(&n, "ZL = conj(Zth) = 500 - j500 mohm")) {
        puts("FAIL p11.15 conjugate load"); failures++;
    } else puts("ok   p11.15 conjugate load");

    c[0] = comp(CK_VSRC, 1, 0, 220, 0);
    c[1] = comp(CK_Z, 1, 0, 124, 0);
    c[2] = comp(CK_Z, 1, 0, 20, -25);
    c[3] = comp(CK_Z, 1, 0, 90, 80);
    narrate_ac_power(c, 4, 2, 1.0, 0, false, true, &n);
    dump_if_requested("Problema 11.38", &n);
    complete("p11.38 narration", &n, "Fasores RMS", "P = 1.635 kW");
    if (!contains(&n, "FP = 0.873 adiantado")) {
        puts("FAIL p11.38 power factor"); failures++;
    } else puts("ok   p11.38 power factor");

    c[0] = comp(CK_RES, 1, 2, 4, 0);
    c[1] = comp(CK_Z, 2, 3, 0, 5);
    c[2] = comp(CK_Z, 2, 0, 0, -2);
    c[3] = comp(CK_Z, 3, 0, 0, -2);
    narrate_ac_power_factor(c, 4, 4, 1.0, 1, 0, &n);
    dump_if_requested("Problema 11.41(a)", &n);
    complete("p11.41a narration", &n, "Impedancia equivalente", "FP = 0.555 adiantado");
    c[0] = comp(CK_RES, 1, 0, 1, 0);
    c[1] = comp(CK_Z, 1, 2, 0, -1);
    c[2] = comp(CK_Z, 2, 0, 0, 2);
    c[3] = comp(CK_RES, 2, 3, 4, 0);
    c[4] = comp(CK_Z, 3, 0, 0, 1);
    narrate_ac_power_factor(c, 5, 4, 1.0, 1, 0, &n);
    dump_if_requested("Problema 11.41(b)", &n);
    complete("p11.41b narration", &n, "Impedancia equivalente", "FP = 0.93 atrasado");

    narrate_power_profile(2, p11_53, 10, &n);
    dump_if_requested("Problema 11.53", &n);
    complete("p11.53 narration", &n, "St = SA + SB + SC", "I = 47 A /_29.8 deg");
    narrate_power_profile(3, p11_69, 4, &n);
    dump_if_requested("Problema 11.69", &n);
    complete("p11.69 narration", &n, "Correcao para FP=1", "C = 130.5 uF");

    narrate_three_phase_profile(4, p12_7, 6, &n);
    dump_if_requested("Problema 12.7", &n);
    complete("p12.7 narration", &n, "Ia = Va/(Zlinha+ZY)", "Ia = 44 A /_53.13 deg");
    narrate_three_phase_profile(2, p12_14, 6, &n);
    dump_if_requested("Problema 12.14", &n);
    complete("p12.14 narration", &n, "Delta equivalente em Y", "Ia = 12.8 A /_-50.19 deg");
    narrate_three_phase_profile(3, p12_25, 6, &n);
    dump_if_requested("Problema 12.25", &n);
    complete("p12.25 narration", &n, "Impedancia por fase", "Ia = 17.74 A /_4.775 deg");
}

static void chapters11_12(void) {
    Narration n;
    float p11[] = {165, 0, 120, 60, 1};
    float p12[] = {4800, 208, 0.9f, 0, 1};
    narrate_max_power(p11, 5, &n);
    dump_if_requested("Capitulo 11", &n);
    if (!contains(&n, "28.36 W")) { puts("FAIL cap11 Pmax"); failures++; }
    else puts("ok   cap11 Pmax");
    complete("cap11 narration", &n, "Vrms = Vpico / sqrt(2)",
             "Pmax = 28.36 W");
    narrate_three_phase(p12, 5, &n);
    dump_if_requested("Capitulo 12", &n);
    if (!contains(&n, "7.692 A") || !contains(&n, "360.3 V")) {
        puts("FAIL cap12 line values"); failures++;
    } else puts("ok   cap12 line values");
    complete("cap12 narration", &n, "Ifase = |S3f| / (3 Vfase)",
             "Ilinha=7.692 A; Vlinha=360.3 V");
}

int main(void) {
    chapter9(); selected_chapter9(); chapter10(); selected_chapter10(); chapters11_12();
    selected_chapters11_12();
    if (failures) { printf("%d failure(s)\n", failures); return 1; }
    puts("ALL NEW-CATALOG CHECKS OK"); return 0;
}
