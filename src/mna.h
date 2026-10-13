/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */

/* Generic modified-nodal-analysis (MNA) linear solver. Portable C (no
 * calculator headers) so it can be unit-tested on the desktop with gcc
 * before being linked into the ez80-clang CE build. See
 * .ai-tasks/spec_v4_engine.md section 3-4 for the design. */
#ifndef CV4_MNA_H
#define CV4_MNA_H

#include <stdbool.h>
#include <stdint.h>

#define MNA_MAXNODES 9   /* node ids 0..8, 0 = ground/reference */
#define MNA_MAXELEM  20  /* max circuit elements (= max editable components) */
#define MNA_MAXDIM   16  /* (MNA_MAXNODES-1) + max V-type unknowns */

/* Phasor (AC) analysis writes the complex system
 *     (G + jB)(Vr + jVi) = (Ir + jIi)
 * as the real block system
 *     [ G  -B ] [ Vr ]   [ Ir ]
 *     [ B   G ] [ Vi ] = [ Ii ]
 * so the SAME Gaussian eliminator solves it with no changes. Deliberately
 * not <complex.h>: the ez80 toolchain does not guarantee _Complex support,
 * and staying in plain real arithmetic keeps this file testable with desktop
 * gcc (tests/test_mna.c). Cost is a matrix of twice the dimension. */
#define MNA_MAXDIM_AC (2 * MNA_MAXDIM)

/* PRECISION. On the ez80 toolchain `double` is 4 bytes (verified:
 * ez80-clang defines __SIZEOF_DOUBLE__ 4), so on the calculator this solver
 * really runs at float precision - about 7 decimal digits. Desktop gcc uses
 * 8-byte doubles, which would hide any precision problem the device would
 * actually hit, and the AC path doubles the matrix dimension, which makes
 * that risk worse rather than better.
 *
 * So the arithmetic type is named, and the desktop tests can force the
 * device's precision:
 *     gcc -DMNA_FORCE_FLOAT ... tests/test_mna.c src/mna.c -lm
 * Both configurations are expected to pass; that is what proves the answers
 * survive 4-byte arithmetic. */
#ifdef MNA_FORCE_FLOAT
typedef float mna_real;
#else
typedef double mna_real;
#endif
typedef enum {
    EK_R = 0,     /* resistor, na/nb order irrelevant */
    EK_VSRC,      /* independent V source, na = "+" terminal */
    EK_ISRC,      /* independent I source, value flows na -> nb inside the source
                     (i.e. injected INTO nb, drawn OUT of na, in the external circuit) */
    EK_VCVS,      /* dependent V source, na = "+"; value = gain * (V[ctrl_a]-V[ctrl_b]) */
    EK_CCVS,      /* dependent V source, na = "+"; value = gain * I[ctrl] (ctrl must be EK_VSRC/EK_VCVS/EK_CCVS) */
    EK_VCCS,      /* dependent I source na->nb; value = gain * (V[ctrl_a]-V[ctrl_b]) */
    EK_CCCS,      /* dependent I source na->nb; value = gain * I[ctrl] */
    /* AC-only kinds; appended so the numbering of everything above is
     * untouched. `value` carries the PHYSICAL quantity (henries / farads),
     * not an impedance - the reactance is derived from the topology's omega
     * at stamp time, which is what makes frequency an editable parameter. */
    EK_L,         /* inductor, value = L in henries  -> Y = -j/(wL) */
    EK_C,         /* capacitor, value = C in farads  -> Y = +jwC    */
    EK_Z,         /* direct impedance value + j*value_im in ohms    */
    EK_OPAMP      /* ideal V+=V-, zero input currents; na is output */
} ElemKind;

typedef struct {
    uint8_t kind;      /* ElemKind */
    uint8_t na, nb;    /* node ids, 0 = ground */
    uint8_t ctrl;      /* controlling element index (dependent sources only), 0xFF = n/a */
    uint8_t ctrl_a, ctrl_b; /* controlling node pair, used when ctrl==0xFF but kind is V*CS
                               referencing a plain node-voltage difference directly */
    mna_real value;      /* ohms / volts / amps / henries / farads / gain, sign already
                           applied by the caller (edits flip a component's `flags`; the
                           caller negates value before calling mna_solve so this solver
                           never branches on flags) */
    mna_real value_im;   /* imaginary part, AC only: the "j" part of a phasor source or of
                           a complex gain. Zero for every DC element - which is why it
                           sits last, so existing positional initialisers stay valid. */
} MnaElem;

typedef struct {
    uint8_t n_nodes;          /* including ground; nodes are 0..n_nodes-1 */
    uint8_t n_elems;
    mna_real omega;             /* rad/s. ZERO selects the original real DC path,
                                 bit-for-bit unchanged; nonzero selects phasor analysis. */
    MnaElem elems[MNA_MAXELEM];
} MnaTopology;

typedef struct {
    mna_real node_v[MNA_MAXNODES];  /* node_v[0] = 0 always */
    mna_real elem_i[MNA_MAXELEM];   /* current through element i, na->nb reference direction;
                                      valid for every element kind (R/ISRC computed directly,
                                      V-type read from their MNA unknown) */
    /* Imaginary parts, populated only when the topology's omega != 0. A DC
     * solve leaves these zeroed, so a caller that ignores them keeps working. */
    mna_real node_v_im[MNA_MAXNODES];
    mna_real elem_i_im[MNA_MAXELEM];
    bool ok;
} MnaResult;

/* Solve the topology as-is (all elements active). Returns false (out->ok=false)
 * on a singular/near-singular system - caller should report "impossivel" and
 * try mna_solve_zeroed() with other sources zeroed, or another content. */
bool mna_solve(const MnaTopology *t, MnaResult *out);

/* Superposition helper: solve with every EK_VSRC/EK_ISRC element EXCEPT
 * `keep_elem` forced to zero (dependent sources and resistors stay active,
 * matching the textbook rule that only independent sources get deactivated). */
bool mna_solve_only(const MnaTopology *t, uint8_t keep_elem, MnaResult *out);

/* Thevenin/Norton helper: zero every independent source, inject a 1A test
 * current source between (port_a, port_b) (port_a=+, current enters port_a
 * from outside), solve; Rth = out->node_v[port_a]-out->node_v[port_b]. */
bool mna_solve_test_source(const MnaTopology *t, uint8_t port_a, uint8_t port_b,
                            MnaResult *out);

#endif
