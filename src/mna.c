/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */

#include "mna.h"
#include <string.h>
#include <math.h>

#define PIVOT_EPS 1e-9

static int nidx(uint8_t node) {
    return node == 0 ? -1 : (int)node - 1;
}

/* Assign an extra MNA unknown (its own current) to every element whose
 * branch equation is a *constraint* (V-type): VSRC, VCVS, CCVS. */
static uint8_t assign_vidx(const MnaTopology *t, uint8_t *vidx, uint8_t base) {
    uint8_t i;
    uint8_t next = base;
    for (i = 0; i < t->n_elems; i++) {
        uint8_t k = t->elems[i].kind;
        if (k == EK_VSRC || k == EK_VCVS || k == EK_CCVS || k == EK_OPAMP) {
            vidx[i] = next++;
        } else {
            vidx[i] = 0xFF;
        }
    }
    return next; /* = total dim */
}

/* One matrix serves both paths: DC uses the top-left MNA_MAXDIM corner, AC
 * uses the whole thing. Sharing it costs DC nothing but a larger row stride
 * and avoids carrying two big static arrays. */
typedef mna_real MnaMatrix[MNA_MAXDIM_AC][MNA_MAXDIM_AC + 1];

static void add_a(MnaMatrix A, int r, int c, mna_real v) {
    if (r < 0 || c < 0) return;
    A[r][c] += v;
}

static void add_b(MnaMatrix A, int r, int dim, mna_real v) {
    if (r < 0) return;
    A[r][dim] += v;
}

static bool solve_linear(MnaMatrix A, int dim, mna_real *x) {
    int i, j, k, piv;
    if (dim == 0) return true;
    if (dim > MNA_MAXDIM_AC) return false;

    for (i = 0; i < dim; i++) {
        mna_real best = fabs(A[i][i]);
        piv = i;
        for (k = i + 1; k < dim; k++) {
            if (fabs(A[k][i]) > best) { best = fabs(A[k][i]); piv = k; }
        }
        if (best < PIVOT_EPS) return false;
        if (piv != i) {
            for (j = 0; j <= dim; j++) {
                mna_real tmp = A[i][j];
                A[i][j] = A[piv][j];
                A[piv][j] = tmp;
            }
        }
        for (k = i + 1; k < dim; k++) {
            mna_real f = A[k][i] / A[i][i];
            if (f == 0.0) continue;
            for (j = i; j <= dim; j++) A[k][j] -= f * A[i][j];
        }
    }
    for (i = dim - 1; i >= 0; i--) {
        mna_real s = A[i][dim];
        for (j = i + 1; j < dim; j++) s -= A[i][j] * x[j];
        x[i] = s / A[i][i];
    }
    return true;
}

static MnaMatrix A;
static mna_real x[MNA_MAXDIM_AC];

static bool stamp_and_solve(const MnaTopology *t, const bool *active, MnaResult *out) {
    uint8_t vidx[MNA_MAXELEM];
    int dim, i;

    memset(A, 0, sizeof(A));
    memset(out, 0, sizeof(*out));
    dim = (int)assign_vidx(t, vidx, (uint8_t)(t->n_nodes - 1));
    if (dim > MNA_MAXDIM) return false;

    for (i = 0; i < t->n_elems; i++) {
        const MnaElem *e = &t->elems[i];
        int na = nidx(e->na), nb = nidx(e->nb);
        mna_real val = (active && !active[i]) ? 0.0 : e->value;

        switch (e->kind) {
        case EK_R: {
            mna_real g = (fabs(val) < 1e-12) ? 1e12 : 1.0 / val;
            add_a(A, na, na, g);
            add_a(A, nb, nb, g);
            add_a(A, na, nb, -g);
            add_a(A, nb, na, -g);
            break;
        }
        case EK_ISRC:
            add_b(A, nb, dim, val);
            add_b(A, na, dim, -val);
            break;
        case EK_VSRC: {
            int row = vidx[i];
            add_a(A, row, na, 1.0);
            add_a(A, row, nb, -1.0);
            add_b(A, row, dim, val);
            add_a(A, na, row, 1.0);
            add_a(A, nb, row, -1.0);
            break;
        }
        case EK_OPAMP: {
            int row = vidx[i];
            add_a(A, row, nidx(e->ctrl_a), 1.0);
            add_a(A, row, nidx(e->ctrl_b), -1.0);
            add_a(A, na, row, 1.0);
            add_a(A, nb, row, -1.0);
            break;
        }
        case EK_VCVS: {
            int row = vidx[i];
            int ca = nidx(e->ctrl_a), cb = nidx(e->ctrl_b);
            add_a(A, row, na, 1.0);
            add_a(A, row, nb, -1.0);
            add_a(A, row, ca, -val);
            add_a(A, row, cb, val);
            add_a(A, na, row, 1.0);
            add_a(A, nb, row, -1.0);
            break;
        }
        case EK_CCVS: {
            int row = vidx[i];
            const MnaElem *c = &t->elems[e->ctrl];
            add_a(A, row, na, 1.0);
            add_a(A, row, nb, -1.0);
            if (e->ctrl != 0xFF && vidx[e->ctrl] != 0xFF) {
                add_a(A, row, vidx[e->ctrl], -val);
            } else {
                int cca = nidx(c->na), ccb = nidx(c->nb);
                mna_real gg = val / c->value;
                add_a(A, row, cca, -gg);
                add_a(A, row, ccb, gg);
            }
            add_a(A, na, row, 1.0);
            add_a(A, nb, row, -1.0);
            break;
        }
        case EK_VCCS: {
            int ca = nidx(e->ctrl_a), cb = nidx(e->ctrl_b);
            /* Current is defined na -> nb.  Its dependent value belongs on
               the RHS like an independent current source; moving it to the
               matrix therefore gives +g at na and -g at nb. */
            add_a(A, na, ca, val);
            add_a(A, na, cb, -val);
            add_a(A, nb, ca, -val);
            add_a(A, nb, cb, val);
            break;
        }
        case EK_CCCS: {
            const MnaElem *c = &t->elems[e->ctrl];
            if (e->ctrl != 0xFF && vidx[e->ctrl] != 0xFF) {
                add_a(A, na, vidx[e->ctrl], val);
                add_a(A, nb, vidx[e->ctrl], -val);
            } else {
                int cca = nidx(c->na), ccb = nidx(c->nb);
                mna_real gg = val / c->value;
                add_a(A, na, cca, gg);
                add_a(A, na, ccb, -gg);
                add_a(A, nb, cca, -gg);
                add_a(A, nb, ccb, gg);
            }
            break;
        }
        default:
            break;
        }
    }

    if (!solve_linear(A, dim, x)) { out->ok = false; return false; }

    out->node_v[0] = 0.0;
    for (i = 0; i < t->n_nodes - 1; i++) out->node_v[i + 1] = x[i];

    for (i = 0; i < t->n_elems; i++) {
        const MnaElem *e = &t->elems[i];
        mna_real val = (active && !active[i]) ? 0.0 : e->value;
        if (vidx[i] != 0xFF) {
            out->elem_i[i] = x[vidx[i]];
        } else if (e->kind == EK_R) {
            out->elem_i[i] = (out->node_v[e->na] - out->node_v[e->nb]) / val;
        } else if (e->kind == EK_ISRC) {
            out->elem_i[i] = val;
        } else if (e->kind == EK_VCCS) {
            out->elem_i[i] = val * (out->node_v[e->ctrl_a] - out->node_v[e->ctrl_b]);
        } else if (e->kind == EK_CCCS) {
            out->elem_i[i] = val * out->elem_i[e->ctrl];
        }
    }
    out->ok = true;
    return true;
}

/* ---- phasor (AC) path ---------------------------------------------------
 * Everything below runs only when topology.omega != 0. The DC code above is
 * left untouched so an existing DC solve cannot change by a single bit. */

/* Stamp the complex value (re + j*im) at complex position (r,c) of the
 * doubled real system. `dc` is the COMPLEX dimension, so the imaginary half
 * of unknown k lives at row/column dc+k and the RHS column is at 2*dc. */
static void add_y(MnaMatrix M, int r, int c, mna_real re, mna_real im, int dc) {
    if (r < 0 || c < 0) return;
    M[r][c]           += re;
    M[r][c + dc]      -= im;
    M[r + dc][c]      += im;
    M[r + dc][c + dc] += re;
}

static void add_rhs(MnaMatrix M, int r, mna_real re, mna_real im, int dc) {
    if (r < 0) return;
    M[r][2 * dc]      += re;
    M[r + dc][2 * dc] += im;
}

static void cmul(mna_real ar, mna_real ai, mna_real br, mna_real bi,
                 mna_real *cr, mna_real *ci) {
    *cr = ar * br - ai * bi;
    *ci = ar * bi + ai * br;
}

/* Admittance of a passive element at omega. R/L/C all collapse to a complex
 * Y here, which is the whole reason frequency can be an editable parameter:
 * the stored value stays physical (ohms/henries/farads) and the reactance is
 * recomputed on every solve. */
static void elem_admittance(const MnaElem *e, mna_real w, mna_real *gr, mna_real *gi) {
    *gr = 0.0;
    *gi = 0.0;
    switch (e->kind) {
    case EK_R:
        if (fabs(e->value) < 1e-12) *gr = 1e12;      /* 0 ohm -> short */
        else *gr = 1.0 / e->value;
        break;
    case EK_L: {
        mna_real wl = w * e->value;
        if (fabs(wl) < 1e-12) *gr = 1e12;            /* wL -> 0 : short */
        else *gi = -1.0 / wl;
        break;
    }
    case EK_C:
        *gi = w * e->value;                          /* C -> 0 : open (Y=0) */
        break;
    case EK_Z: {
        mna_real den = e->value * e->value + e->value_im * e->value_im;
        if (den < 1e-24) *gr = 1e12;
        else { *gr = e->value / den; *gi = -e->value_im / den; }
        break;
    }
    default:
        break;
    }
}

static bool stamp_and_solve_ac(const MnaTopology *t, const bool *active,
                               MnaResult *out) {
    uint8_t vidx[MNA_MAXELEM];
    int dimc, i;
    mna_real w = t->omega;

    memset(A, 0, sizeof(A));
    memset(out, 0, sizeof(*out));
    dimc = (int)assign_vidx(t, vidx, (uint8_t)(t->n_nodes - 1));
    if (dimc > MNA_MAXDIM) return false;

    for (i = 0; i < t->n_elems; i++) {
        const MnaElem *e = &t->elems[i];
        int na = nidx(e->na), nb = nidx(e->nb);
        bool off = (active && !active[i]);
        mna_real vr = off ? 0.0 : e->value;
        mna_real vi = off ? 0.0 : e->value_im;

        switch (e->kind) {
        case EK_R: case EK_L: case EK_C: case EK_Z: {
            mna_real gr, gi;
            MnaElem tmp = *e;
            /* a deactivated passive element keeps its impedance - only
               independent SOURCES are zeroed for superposition */
            tmp.value = e->value;
            elem_admittance(&tmp, w, &gr, &gi);
            add_y(A, na, na, gr, gi, dimc);
            add_y(A, nb, nb, gr, gi, dimc);
            add_y(A, na, nb, -gr, -gi, dimc);
            add_y(A, nb, na, -gr, -gi, dimc);
            break;
        }
        case EK_ISRC:
            add_rhs(A, nb, vr, vi, dimc);
            add_rhs(A, na, -vr, -vi, dimc);
            break;
        case EK_VSRC: {
            int row = vidx[i];
            add_y(A, row, na, 1.0, 0.0, dimc);
            add_y(A, row, nb, -1.0, 0.0, dimc);
            add_rhs(A, row, vr, vi, dimc);
            add_y(A, na, row, 1.0, 0.0, dimc);
            add_y(A, nb, row, -1.0, 0.0, dimc);
            break;
        }
        case EK_OPAMP: {
            int row = vidx[i];
            add_y(A, row, nidx(e->ctrl_a), 1.0, 0.0, dimc);
            add_y(A, row, nidx(e->ctrl_b), -1.0, 0.0, dimc);
            add_y(A, na, row, 1.0, 0.0, dimc);
            add_y(A, nb, row, -1.0, 0.0, dimc);
            break;
        }
        case EK_VCVS: {
            int row = vidx[i];
            int ca = nidx(e->ctrl_a), cb = nidx(e->ctrl_b);
            add_y(A, row, na, 1.0, 0.0, dimc);
            add_y(A, row, nb, -1.0, 0.0, dimc);
            add_y(A, row, ca, -vr, -vi, dimc);
            add_y(A, row, cb, vr, vi, dimc);
            add_y(A, na, row, 1.0, 0.0, dimc);
            add_y(A, nb, row, -1.0, 0.0, dimc);
            break;
        }
        case EK_CCVS: {
            int row = vidx[i];
            add_y(A, row, na, 1.0, 0.0, dimc);
            add_y(A, row, nb, -1.0, 0.0, dimc);
            if (e->ctrl != 0xFF && vidx[e->ctrl] != 0xFF) {
                add_y(A, row, vidx[e->ctrl], -vr, -vi, dimc);
            } else if (e->ctrl != 0xFF) {
                const MnaElem *c = &t->elems[e->ctrl];
                mna_real yr, yi, gmr, gmi;
                int ca = nidx(c->na), cb = nidx(c->nb);
                /* A passive controlling branch has no dedicated MNA current
                   unknown. Use Ictrl=Yctrl(Vca-Vcb), including the complex
                   admittance of C/L/Z, then stamp
                   Vna-Vnb-gain*Ictrl=0. */
                elem_admittance(c, w, &yr, &yi);
                cmul(vr, vi, yr, yi, &gmr, &gmi);
                add_y(A, row, ca, -gmr, -gmi, dimc);
                add_y(A, row, cb, gmr, gmi, dimc);
            }
            add_y(A, na, row, 1.0, 0.0, dimc);
            add_y(A, nb, row, -1.0, 0.0, dimc);
            break;
        }
        case EK_VCCS: {
            int ca = nidx(e->ctrl_a), cb = nidx(e->ctrl_b);
            add_y(A, na, ca, vr, vi, dimc);
            add_y(A, na, cb, -vr, -vi, dimc);
            add_y(A, nb, ca, -vr, -vi, dimc);
            add_y(A, nb, cb, vr, vi, dimc);
            break;
        }
        case EK_CCCS:
            if (e->ctrl != 0xFF && vidx[e->ctrl] != 0xFF) {
                add_y(A, na, vidx[e->ctrl], vr, vi, dimc);
                add_y(A, nb, vidx[e->ctrl], -vr, -vi, dimc);
            } else if (e->ctrl != 0xFF) {
                const MnaElem *c = &t->elems[e->ctrl];
                mna_real yr, yi, gmr, gmi;
                int ca = nidx(c->na), cb = nidx(c->nb);
                elem_admittance(c, w, &yr, &yi);
                cmul(vr, vi, yr, yi, &gmr, &gmi);
                add_y(A, na, ca, gmr, gmi, dimc);
                add_y(A, na, cb, -gmr, -gmi, dimc);
                add_y(A, nb, ca, -gmr, -gmi, dimc);
                add_y(A, nb, cb, gmr, gmi, dimc);
            }
            break;
        default:
            break;
        }
    }

    if (!solve_linear(A, 2 * dimc, x)) { out->ok = false; return false; }

    out->node_v[0] = 0.0;
    out->node_v_im[0] = 0.0;
    for (i = 0; i < t->n_nodes - 1; i++) {
        out->node_v[i + 1] = x[i];
        out->node_v_im[i + 1] = x[dimc + i];
    }

    for (i = 0; i < t->n_elems; i++) {
        const MnaElem *e = &t->elems[i];
        bool off = (active && !active[i]);
        mna_real vr = off ? 0.0 : e->value;
        mna_real vi = off ? 0.0 : e->value_im;

        if (vidx[i] != 0xFF) {
            out->elem_i[i] = x[vidx[i]];
            out->elem_i_im[i] = x[dimc + vidx[i]];
        } else if (e->kind == EK_R || e->kind == EK_L || e->kind == EK_C || e->kind == EK_Z) {
            mna_real gr, gi, dvr, dvi;
            elem_admittance(e, w, &gr, &gi);
            dvr = out->node_v[e->na] - out->node_v[e->nb];
            dvi = out->node_v_im[e->na] - out->node_v_im[e->nb];
            cmul(dvr, dvi, gr, gi, &out->elem_i[i], &out->elem_i_im[i]);
        } else if (e->kind == EK_ISRC) {
            out->elem_i[i] = vr;
            out->elem_i_im[i] = vi;
        } else if (e->kind == EK_VCCS) {
            mna_real dvr = out->node_v[e->ctrl_a] - out->node_v[e->ctrl_b];
            mna_real dvi = out->node_v_im[e->ctrl_a] - out->node_v_im[e->ctrl_b];
            cmul(vr, vi, dvr, dvi, &out->elem_i[i], &out->elem_i_im[i]);
        } else if (e->kind == EK_CCCS && e->ctrl != 0xFF) {
            cmul(vr, vi, out->elem_i[e->ctrl], out->elem_i_im[e->ctrl],
                 &out->elem_i[i], &out->elem_i_im[i]);
        }
    }
    out->ok = true;
    return true;
}

static bool dispatch(const MnaTopology *t, const bool *active, MnaResult *out) {
    if (t->omega != 0.0) return stamp_and_solve_ac(t, active, out);
    return stamp_and_solve(t, active, out);
}

bool mna_solve(const MnaTopology *t, MnaResult *out) {
    return dispatch(t, NULL, out);
}

bool mna_solve_only(const MnaTopology *t, uint8_t keep_elem, MnaResult *out) {
    bool active[MNA_MAXELEM];
    uint8_t i;
    for (i = 0; i < t->n_elems; i++) {
        uint8_t k = t->elems[i].kind;
        bool independent = (k == EK_VSRC || k == EK_ISRC);
        active[i] = (!independent) || (i == keep_elem);
    }
    return dispatch(t, active, out);
}

bool mna_solve_test_source(const MnaTopology *t, uint8_t port_a, uint8_t port_b,
                            MnaResult *out) {
    static MnaTopology t2;
    static bool active[MNA_MAXELEM];
    uint8_t i;

    t2 = *t;

    for (i = 0; i < t2.n_elems; i++) {
        uint8_t k = t2.elems[i].kind;
        active[i] = !(k == EK_VSRC || k == EK_ISRC);
    }
    if (t2.n_elems >= MNA_MAXELEM) return false;
    t2.elems[t2.n_elems].kind = EK_ISRC;
    t2.elems[t2.n_elems].na = port_b;   /* current enters port_a (see header) */
    t2.elems[t2.n_elems].nb = port_a;
    t2.elems[t2.n_elems].value = 1.0;
    t2.elems[t2.n_elems].value_im = 0.0;   /* 1+j0 A test source */
    active[t2.n_elems] = true;
    t2.n_elems++;
    return dispatch(&t2, active, out);
}
