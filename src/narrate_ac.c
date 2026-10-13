/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */

#include "narrate_ac.h"
#include "narrate.h"
#include "fmt.h"
#include <string.h>
#include <math.h>

/* Append a complex quantity in polar form (the form a textbook answer is
 * always given in), using fmt.c so there is one place that decides how a
 * phasor prints. */
static void lb_polar(LineBuf *lb, double re, double im, const char *unit) {
    char tmp[40];
    fmt_polar(tmp, re, im, unit);
    lb_str(lb, tmp);
}

static void lb_rect(LineBuf *lb, double re, double im, const char *unit) {
    char tmp[40];
    fmt_rect(tmp, re, im, unit);
    lb_str(lb, tmp);
}

static void comp_tag(LineBuf *lb, const EditComp *c, uint8_t within) {
    char d[4];
    switch (c->kind) {
    case CK_RES: lb_str(lb, "R"); break;
    case CK_CAP: lb_str(lb, "C"); break;
    case CK_IND: lb_str(lb, "L"); break;
    case CK_VSRC: lb_str(lb, "V"); break;
    case CK_ISRC: lb_str(lb, "I"); break;
    default: lb_str(lb, "X"); break;
    }
    d[0] = (char)('0' + (within % 10));
    d[1] = '\0';
    lb_str(lb, d);
}

static void node_tag(LineBuf *lb, const char *const *labels, uint8_t node) {
    char d[4];
    if (node == 0) { lb_str(lb, "0"); return; }
    if (labels && labels[node]) { lb_str(lb, labels[node]); return; }
    lb_str(lb, "V");
    d[0] = (char)('0' + node % 10); d[1] = '\0';
    lb_str(lb, d);
}

static bool fixed_source(const EditComp *comps, uint8_t n, uint8_t node,
                         double *re, double *im) {
    uint8_t i;
    for (i = 0; i < n; i++) {
        const EditComp *c = &comps[i];
        double sign;
        if (c->kind != CK_VSRC) continue;
        if (c->na == node && c->nb == 0) sign = 1.0;
        else if (c->nb == node && c->na == 0) sign = -1.0;
        else continue;
        if (c->flags & 1) sign = -sign;
        *re = sign * c->value; *im = sign * c->value_im;
        return true;
    }
    return false;
}

/* Impedance of one passive component at omega, as re + j*im. */
static bool comp_impedance(const EditComp *c, double w, double *zr, double *zi) {
    *zr = 0.0;
    *zi = 0.0;
    switch (c->kind) {
    case CK_RES: *zr = c->value; return true;
    case CK_IND: *zi = w * c->value; return true;               /* jwL     */
    case CK_Z: *zr = c->value; *zi = c->value_im; return true;
    case CK_CAP:
        if (fabs(w * c->value) < 1e-15) return false;
        *zi = -1.0 / (w * c->value);                            /* -j/(wC) */
        return true;
    default: return false;
    }
}

/* Shared preamble: state the frequency, then list every passive element's
 * impedance. This is the step a student is actually graded on, so it is
 * narrated before any solving happens. */
static void narrate_impedance_table(const EditComp *comps, uint8_t n, double w,
                                    Narration *out) {
    LineBuf lb;
    uint8_t i, seen = 0;
    bool physical_reactive = false;

    for (i = 0; i < n; i++)
        if (comps[i].kind == CK_CAP || comps[i].kind == CK_IND)
            physical_reactive = true;

    lb_reset(&lb);
    lb_str(&lb, "# 1) Impedancias no dominio fasorial");
    narrate_commit(out, NCOL_BLUE, &lb);

    if (physical_reactive) {
        lb_reset(&lb); lb_str(&lb, "w = "); lb_eng(&lb, w, "rad/s");
        narrate_commit(out, NCOL_BLACK, &lb);
    }

    for (i = 0; i < n; i++) {
        const EditComp *c = &comps[i];
        double zr, zi;
        if (c->kind != CK_CAP && c->kind != CK_IND && c->kind != CK_Z) continue;
        if (!comp_impedance(c, w, &zr, &zi)) continue;
        seen++;
        lb_reset(&lb);
        lb_str(&lb, "Z(");
        comp_tag(&lb, c, seen);
        if (c->kind == CK_Z) {
            lb_str(&lb, ") = ");
        } else {
            lb_str(&lb, " = ");
            lb_eng(&lb, c->value, unit_for_kind(c->kind));
            lb_str(&lb, ") = ");
        }
        lb_rect(&lb, zr, zi, "ohm");
        narrate_commit(out, NCOL_BLACK, &lb);
    }
}

bool narrate_ac_nodal(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                      double omega, const char *const *node_label, uint8_t target,
                      bool target_voltage,
                      Narration *out) {
    MnaTopology topo;
    MnaResult res;
    uint8_t elem_of[COMP_MAXN];
    uint8_t k, i;
    LineBuf lb;

    narrate_reset(out);
    if (omega == 0.0) {
        return narrate_mark_impossible(out, "frequencia zero: use analise DC");
    }

    topo.n_nodes = n_nodes;
    build_mna_ac(comps, n, omega, &topo, elem_of);
    if (!mna_solve(&topo, &res)) {
        /* must stay <= 39 chars: audit_strings.py enforces the C literal
           limit, and NARRATE_LINEWIDTH would truncate a longer one anyway */
        return narrate_mark_impossible(out, "sistema singular (curto ou fonte ma)");
    }

    narrate_impedance_table(comps, n, omega, out);

    lb_reset(&lb); lb_str(&lb, "# 2) Fonte e referencia");
    narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, "V0 = 0 V"); narrate_commit(out, NCOL_BLACK, &lb);

    for (k = 1; k < n_nodes; k++) {
        double fr, fi;
        if (!fixed_source(comps, n, k, &fr, &fi)) continue;
        lb_reset(&lb);
        node_tag(&lb, node_label, k); lb_str(&lb, " = ");
        lb_polar(&lb, fr, fi, "V"); lb_str(&lb, " (fonte)");
        narrate_commit(out, NCOL_BLACK, &lb);
    }

    for (k = 1; k < n_nodes; k++) {
        double fr, fi;
        if (fixed_source(comps, n, k, &fr, &fi)) continue;
        lb_reset(&lb); lb_str(&lb, "# 3) KCL no no ");
        node_tag(&lb, node_label, k); narrate_commit(out, NCOL_BLUE, &lb);
        for (i = 0; i < n; i++) {
            const EditComp *c = &comps[i];
            uint8_t other;
            double zr, zi;
            if (c->na != k && c->nb != k) continue;
            if (!comp_impedance(c, omega, &zr, &zi)) continue;
            other = c->na == k ? c->nb : c->na;
            lb_reset(&lb); lb_str(&lb, "("); node_tag(&lb, node_label, k);
            lb_str(&lb, " - "); node_tag(&lb, node_label, other);
            lb_str(&lb, ") / ("); lb_rect(&lb, zr, zi, ""); lb_str(&lb, ")");
            narrate_commit(out, NCOL_BLACK, &lb);
        }
        lb_reset(&lb); lb_str(&lb, "Soma das correntes = 0");
        narrate_commit(out, NCOL_BLACK, &lb);
    }

    lb_reset(&lb); lb_str(&lb, "# 4) Solucao do sistema");
    narrate_commit(out, NCOL_BLUE, &lb);
    for (k = 1; k < n_nodes; k++) {
        double fr, fi;
        if (fixed_source(comps, n, k, &fr, &fi)) continue;
        lb_reset(&lb);
        node_tag(&lb, node_label, k); lb_str(&lb, " = ");
        lb_rect(&lb, res.node_v[k], res.node_v_im[k], "V");
        narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb);
        lb_str(&lb, "   = "); lb_polar(&lb, res.node_v[k], res.node_v_im[k], "V");
        narrate_commit(out, NCOL_BLACK, &lb);
    }
    if (target < n && elem_of[target] != 0xFF) {
        const EditComp *c = &comps[target];
        uint8_t e = elem_of[target];
        double zr, zi;
        lb_reset(&lb); lb_str(&lb, target_voltage ? "# 5) Tensao pedida" : "# 5) Corrente pedida");
        narrate_commit(out, NCOL_BLUE, &lb);
        if (target_voltage) {
            double vr = res.node_v[c->na] - res.node_v[c->nb];
            double vi = res.node_v_im[c->na] - res.node_v_im[c->nb];
            lb_reset(&lb); lb_str(&lb, "Vo = "); node_tag(&lb, node_label, c->na);
            lb_str(&lb, " - "); node_tag(&lb, node_label, c->nb);
            narrate_commit(out, NCOL_BLACK, &lb);
            lb_reset(&lb); lb_str(&lb, "Vo = "); lb_rect(&lb, vr, vi, "V");
            narrate_commit(out, NCOL_BLACK, &lb);
            lb_reset(&lb); lb_str(&lb, "Vo = "); lb_polar(&lb, vr, vi, "V");
            narrate_commit(out, NCOL_RED, &lb);
            return true;
        }
        lb_reset(&lb); lb_str(&lb, "Io = ("); node_tag(&lb, node_label, c->na);
        lb_str(&lb, " - "); node_tag(&lb, node_label, c->nb); lb_str(&lb, ") / (");
        if (comp_impedance(c, omega, &zr, &zi)) lb_rect(&lb, zr, zi, "");
        else lb_str(&lb, "Z");
        lb_str(&lb, ")"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "Io = ");
        lb_rect(&lb, res.elem_i[e], res.elem_i_im[e], "A");
        narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "Io = ");
        lb_polar(&lb, res.elem_i[e], res.elem_i_im[e], "A");
        narrate_commit(out, NCOL_RED, &lb);
    }
    return true;
}

bool narrate_ac_mesh(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                     double omega, const MeshEdge *const *meshes,
                     const uint8_t *mesh_len, uint8_t n_meshes,
                     uint8_t target,
                     Narration *out) {
    MnaTopology topo;
    MnaResult res;
    uint8_t elem_of[COMP_MAXN];
    uint8_t i, j, k;
    LineBuf lb;
    narrate_reset(out);
    if (!n_meshes) return narrate_mark_impossible(out, "nenhuma malha independente");
    topo.n_nodes = n_nodes;
    build_mna_ac(comps, n, omega, &topo, elem_of);
    if (!mna_solve(&topo, &res)) return narrate_mark_impossible(out, "sistema de malhas singular");
    lb_reset(&lb); lb_str(&lb, "# Correntes de malha (fasores):"); narrate_commit(out, NCOL_BLUE, &lb);
    for (i = 0; i < n_meshes; i++) {
        const MeshEdge *chosen = 0;
        for (j = 0; j < mesh_len[i] && !chosen; j++) {
            uint8_t occurrences = 0;
            for (k = 0; k < n_meshes; k++) {
                uint8_t q;
                for (q = 0; q < mesh_len[k]; q++)
                    if (meshes[k][q].elem == meshes[i][j].elem) occurrences++;
            }
            if (occurrences == 1) chosen = &meshes[i][j];
        }
        if (!chosen || chosen->elem >= n || elem_of[chosen->elem] == 0xFF)
            return narrate_mark_impossible(out, "malha sem ramo exclusivo");
        {
            uint8_t e = elem_of[chosen->elem];
            double sign = chosen->sign < 0 ? -1.0 : 1.0;
            char d[3];
            lb_reset(&lb); lb_str(&lb, "I"); d[0] = (char)('1' + i); d[1] = 0;
            lb_str(&lb, d); lb_str(&lb, " = ");
            lb_polar(&lb, sign * res.elem_i[e], sign * res.elem_i_im[e], "A");
            narrate_commit(out, NCOL_RED, &lb);
        }
    }
    if (target < n && elem_of[target] != 0xFF) {
        uint8_t e = elem_of[target];
        lb_reset(&lb); lb_str(&lb, "# Corrente pedida no ramo");
        narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "Io = ");
        lb_rect(&lb, res.elem_i[e], res.elem_i_im[e], "A");
        narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "Io = ");
        lb_polar(&lb, res.elem_i[e], res.elem_i_im[e], "A");
        narrate_commit(out, NCOL_RED, &lb);
    }
    return true;
}

bool narrate_ac_superposition(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                              double omega, uint8_t target, Narration *out) {
    MnaTopology topo;
    MnaResult part;
    uint8_t elem_of[COMP_MAXN], i, target_elem;
    double sum_re = 0.0, sum_im = 0.0;
    LineBuf lb;
    narrate_reset(out);
    if (target >= n) return narrate_mark_impossible(out, "alvo de superposicao invalido");
    topo.n_nodes = n_nodes; build_mna_ac(comps, n, omega, &topo, elem_of);
    target_elem = elem_of[target];
    if (target_elem == 0xFF) return narrate_mark_impossible(out, "alvo nao eletrico");
    lb_reset(&lb); lb_str(&lb, "# Uma fonte independente por vez:"); narrate_commit(out, NCOL_BLUE, &lb);
    for (i = 0; i < topo.n_elems; i++) {
        if (topo.elems[i].kind != EK_VSRC && topo.elems[i].kind != EK_ISRC) continue;
        if (!mna_solve_only(&topo, i, &part)) return narrate_mark_impossible(out, "parcela singular");
        sum_re += part.elem_i[target_elem]; sum_im += part.elem_i_im[target_elem];
        lb_reset(&lb); lb_str(&lb, "Parcela = ");
        lb_polar(&lb, part.elem_i[target_elem], part.elem_i_im[target_elem], "A");
        narrate_commit(out, NCOL_BLACK, &lb);
    }
    lb_reset(&lb); lb_str(&lb, "I total = "); lb_polar(&lb, sum_re, sum_im, "A");
    narrate_commit(out, NCOL_RED, &lb);
    return true;
}

bool narrate_ac_thevenin(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                         double omega, uint8_t port_a, uint8_t port_b,
                         Narration *out) {
    MnaTopology topo;
    MnaResult live, test;
    uint8_t elem_of[COMP_MAXN];
    double vr, vi, zr, zi, den;
    LineBuf lb;
    narrate_reset(out);
    topo.n_nodes = n_nodes; build_mna_ac(comps, n, omega, &topo, elem_of);
    if (!mna_solve(&topo, &live) || !mna_solve_test_source(&topo, port_a, port_b, &test))
        return narrate_mark_impossible(out, "Thevenin indefinido nos terminais");
    vr = live.node_v[port_a] - live.node_v[port_b];
    vi = live.node_v_im[port_a] - live.node_v_im[port_b];
    zr = test.node_v[port_a] - test.node_v[port_b];
    zi = test.node_v_im[port_a] - test.node_v_im[port_b];
    lb_reset(&lb); lb_str(&lb, "Vth = "); lb_polar(&lb, vr, vi, "V"); narrate_commit(out, NCOL_RED, &lb);
    lb_reset(&lb); lb_str(&lb, "Zth = "); lb_rect(&lb, zr, zi, "ohm"); narrate_commit(out, NCOL_RED, &lb);
    den = zr * zr + zi * zi;
    if (den > 1e-18) {
        double nr, ni;
        nr = (vr * zr + vi * zi) / den;
        ni = (vi * zr - vr * zi) / den;
        lb_reset(&lb); lb_str(&lb, "In = Vth/Zth = "); lb_polar(&lb, nr, ni, "A");
        narrate_commit(out, NCOL_BLACK, &lb);
    }
    return true;
}

bool narrate_ac_power(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                      double omega, uint8_t target, bool peak, bool delivered,
                      Narration *out) {
    MnaTopology topo;
    MnaResult res;
    uint8_t elem_of[COMP_MAXN], e;
    double vr, vi, ir, ii, scale, p, q, smag, pf;
    LineBuf lb;
    narrate_reset(out);
    if (target >= n) return narrate_mark_impossible(out, "elemento de potencia invalido");
    topo.n_nodes = n_nodes; build_mna_ac(comps, n, omega, &topo, elem_of);
    e = elem_of[target];
    if (e == 0xFF || !mna_solve(&topo, &res)) return narrate_mark_impossible(out, "potencia nao calculavel");
    vr = res.node_v[comps[target].na] - res.node_v[comps[target].nb];
    vi = res.node_v_im[comps[target].na] - res.node_v_im[comps[target].nb];
    ir = res.elem_i[e]; ii = res.elem_i_im[e]; scale = peak ? 0.5 : 1.0;
    p = scale * (vr * ir + vi * ii); q = scale * (vi * ir - vr * ii);
    if (delivered) { p = -p; q = -q; }
    lb_reset(&lb); lb_str(&lb, peak ? "# Fasores de pico: S=V.I*/2" : "# Fasores RMS: S=V.I*");
    narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, "S = "); lb_rect(&lb, p, q, "VA"); narrate_commit(out, NCOL_RED, &lb);
    lb_reset(&lb); lb_str(&lb, "P = "); lb_eng(&lb, p, "W"); narrate_commit(out, NCOL_RED, &lb);
    lb_reset(&lb); lb_str(&lb, "Q = "); lb_eng(&lb, q, "VAR"); narrate_commit(out, NCOL_RED, &lb);
    smag = sqrt(p * p + q * q);
    pf = smag > 1e-18 ? fabs(p) / smag : 1.0;
    lb_reset(&lb); lb_str(&lb, "FP = "); lb_num(&lb, pf);
    if (fabs(q) <= 1e-7 * (smag + 1.0)) lb_str(&lb, " unitario");
    else lb_str(&lb, q < 0.0 ? " adiantado" : " atrasado");
    narrate_commit(out, NCOL_RED, &lb);
    return true;
}

bool narrate_ac_power_factor(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                             double omega, uint8_t port_a, uint8_t port_b,
                             Narration *out) {
    MnaTopology topo;
    MnaResult test;
    uint8_t elem_of[COMP_MAXN];
    double zr, zi, angle, pf;
    LineBuf lb;

    narrate_reset(out);
    topo.n_nodes = n_nodes;
    build_mna_ac(comps, n, omega, &topo, elem_of);
    if (!mna_solve_test_source(&topo, port_a, port_b, &test))
        return narrate_mark_impossible(out, "impedancia equivalente indefinida");
    zr = test.node_v[port_a] - test.node_v[port_b];
    zi = test.node_v_im[port_a] - test.node_v_im[port_b];
    angle = cx_deg(zr, zi);
    pf = cos(fabs(angle) * 3.14159265358979323846 / 180.0);

    lb_reset(&lb); lb_str(&lb, "# 1) Impedancia equivalente");
    narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, "Zeq = "); lb_rect(&lb, zr, zi, "ohm");
    narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "Zeq = "); lb_polar(&lb, zr, zi, "ohm");
    narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "# 2) FP = cos(|angulo de Z|)");
    narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, "FP = "); lb_num(&lb, pf);
    lb_str(&lb, zi < 0.0 ? " adiantado" : (zi > 0.0 ? " atrasado" : " unitario"));
    narrate_commit(out, NCOL_RED, &lb);
    return true;
}

bool narrate_ac_max_power(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                          double omega, uint8_t port_a, uint8_t port_b,
                          bool peak, Narration *out) {
    MnaTopology topo;
    MnaResult live, test;
    uint8_t elem_of[COMP_MAXN];
    double vr, vi, zr, zi, pmax;
    LineBuf lb;

    narrate_reset(out);
    topo.n_nodes = n_nodes;
    build_mna_ac(comps, n, omega, &topo, elem_of);
    if (!mna_solve(&topo, &live) ||
        !mna_solve_test_source(&topo, port_a, port_b, &test))
        return narrate_mark_impossible(out, "Thevenin indefinido na carga");
    vr = live.node_v[port_a] - live.node_v[port_b];
    vi = live.node_v_im[port_a] - live.node_v_im[port_b];
    zr = test.node_v[port_a] - test.node_v[port_b];
    zi = test.node_v_im[port_a] - test.node_v_im[port_b];
    if (zr <= 1e-9) return narrate_mark_impossible(out, "Rth deve ser positivo");
    pmax = (vr * vr + vi * vi) / ((peak ? 8.0 : 4.0) * zr);

    lb_reset(&lb); lb_str(&lb, "# 1) Equivalente de Thevenin");
    narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, "Vth = "); lb_polar(&lb, vr, vi, "V");
    narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "Zth = "); lb_rect(&lb, zr, zi, "ohm");
    narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "# 2) Casamento conjugado");
    narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, "ZL = conj(Zth) = "); lb_rect(&lb, zr, -zi, "ohm");
    narrate_commit(out, NCOL_RED, &lb);
    lb_reset(&lb); lb_str(&lb, "# 3) Potencia maxima");
    narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, peak ? "Pmax=|Vth|^2/(8 Rth)" : "Pmax=|Vth|^2/(4 Rth)");
    narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "Pmax = "); lb_eng(&lb, pmax, "W");
    narrate_commit(out, NCOL_RED, &lb);
    return true;
}

bool narrate_ac_impedance(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                          double omega, uint8_t port_a, uint8_t port_b,
                          Narration *out) {
    MnaTopology topo;
    MnaResult res;
    uint8_t elem_of[COMP_MAXN];
    LineBuf lb;
    double zr, zi, mag2, yr, yi;
    bool parallel = true;
    uint8_t i, branch = 0;

    narrate_reset(out);
    if (omega == 0.0) {
        return narrate_mark_impossible(out, "frequencia zero: use analise DC");
    }

    /* Direct parallel network: show the textbook admittance method instead
       of hiding the arithmetic behind a test source. */
    for (i = 0; i < n; i++) {
        const EditComp *c = &comps[i];
        double tr, ti;
        bool same_ports;
        if (c->kind == CK_ARROW) continue;
        same_ports = ((c->na == port_a && c->nb == port_b) ||
                      (c->na == port_b && c->nb == port_a));
        if (!same_ports || !comp_impedance(c, omega, &tr, &ti)) {
            parallel = false; break;
        }
        branch++;
    }

    if (parallel && branch > 0) {
        double sum_r = 0.0, sum_i = 0.0;
        uint8_t within = 0;
        lb_reset(&lb); lb_str(&lb, "# 1) Admitancia de cada ramo");
        narrate_commit(out, NCOL_BLUE, &lb);
        for (i = 0; i < n; i++) {
            const EditComp *c = &comps[i];
            double tr, ti, den;
            char d[3];
            if (c->kind == CK_ARROW || !comp_impedance(c, omega, &tr, &ti)) continue;
            within++; d[0] = (char)('0' + within); d[1] = '\0';
            lb_reset(&lb); lb_str(&lb, "Z"); lb_str(&lb, d); lb_str(&lb, " = ");
            lb_rect(&lb, tr, ti, "ohm"); narrate_commit(out, NCOL_BLACK, &lb);
            den = tr * tr + ti * ti;
            if (den < 1e-18) return narrate_mark_impossible(out, "ramo em curto: admitancia infinita");
            yr = tr / den; yi = -ti / den;
            sum_r += yr; sum_i += yi;
            lb_reset(&lb); lb_str(&lb, "Y"); lb_str(&lb, d); lb_str(&lb, " = 1/Z");
            lb_str(&lb, d); lb_str(&lb, " = "); lb_rect(&lb, yr, yi, "S");
            narrate_commit(out, NCOL_BLACK, &lb);
        }
        lb_reset(&lb); lb_str(&lb, "# 2) Ramos em paralelo: somar Y");
        narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "Yeq = ");
        for (i = 1; i <= within; i++) {
            char d[3]; d[0] = (char)('0' + i); d[1] = '\0';
            if (i > 1) lb_str(&lb, " + ");
            lb_str(&lb, "Y"); lb_str(&lb, d);
        }
        narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "Yeq = "); lb_rect(&lb, sum_r, sum_i, "S");
        narrate_commit(out, NCOL_RED, &lb);
        lb_reset(&lb); lb_str(&lb, "    = "); lb_polar(&lb, sum_r, sum_i, "S");
        narrate_commit(out, NCOL_BLACK, &lb);

        mag2 = sum_r * sum_r + sum_i * sum_i;
        zr = sum_r / mag2; zi = -sum_i / mag2;
        lb_reset(&lb); lb_str(&lb, "# 3) Zeq = 1/Yeq"); narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "Zeq = "); lb_rect(&lb, zr, zi, "ohm");
        narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "    = "); lb_polar(&lb, zr, zi, "ohm");
        narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "# Resultado pedido"); narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "Y = "); lb_rect(&lb, sum_r, sum_i, "S");
        narrate_commit(out, NCOL_RED, &lb);
        lb_reset(&lb); lb_str(&lb, "Y = "); lb_polar(&lb, sum_r, sum_i, "S");
        narrate_commit(out, NCOL_RED, &lb);
        return true;
    }

    topo.n_nodes = n_nodes;
    build_mna_ac(comps, n, omega, &topo, elem_of);

    /* 1/_0 A into port_a with every independent source dead: the resulting
       port voltage IS the equivalent impedance. Same method narrate_thevenin
       uses for Rth - it needs no change to work in the complex domain. */
    if (!mna_solve_test_source(&topo, port_a, port_b, &res)) {
        return narrate_mark_impossible(out, "impedancia indefinida neste par de nos");
    }

    narrate_impedance_table(comps, n, omega, out);

    zr = res.node_v[port_a] - res.node_v[port_b];
    zi = res.node_v_im[port_a] - res.node_v_im[port_b];

    lb_reset(&lb);
    lb_str(&lb, "# 2) Fonte-teste de 1 /_0 A");
    narrate_commit(out, NCOL_BLUE, &lb);

    lb_reset(&lb);
    lb_str(&lb, "Zeq = ");
    lb_rect(&lb, zr, zi, "ohm");
    narrate_commit(out, NCOL_RED, &lb);

    lb_reset(&lb);
    lb_str(&lb, "    = ");
    lb_polar(&lb, zr, zi, "ohm");
    narrate_commit(out, NCOL_RED, &lb);

    mag2 = zr * zr + zi * zi;
    if (mag2 > 1e-18) {
        yr = zr / mag2;      /* Y = 1/Z = conj(Z)/|Z|^2 */
        yi = -zi / mag2;
        lb_reset(&lb);
        lb_str(&lb, "Yeq = 1/Zeq = ");
        lb_rect(&lb, yr, yi, "S");
        narrate_commit(out, NCOL_RED, &lb);
    }
    return true;
}
