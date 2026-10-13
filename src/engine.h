/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */

/* CE-specific glue on top of the portable src/mna.h solver: editable
 * components, reduction-program bytecode, mesh derivation and the
 * "narrator" functions that turn a live circuit into step-by-step text.
 * Portable (no calculator headers) except NStep's use of TextLine-style
 * plain buffers, so this is still unit-testable with gcc - see
 * tests/test_narrate.c. */
#ifndef CV4_ENGINE_H
#define CV4_ENGINE_H

#include <stdbool.h>
#include <stdint.h>
#include "mna.h"

typedef enum {
    CK_RES = 0, CK_VSRC, CK_ISRC, CK_CAP, CK_IND, CK_DVS, CK_DIS,
    CK_ARROW, /* not an electrical element - a plain reference-direction
                 arrow (assumed current direction). Carries no na/nb/value;
                 only flags bit0 (direction) is meaningful. Reuses the same
                 comps[]/reg/edit-menu machinery as real components purely
                 so direction-flipping gets the exact same live-edit path,
                 per spec section 2. build_mna() must skip these. */
    CK_Z      /* generic complex impedance: value + j*value_im ohms */
} CompKind;

#define COMP_MAXN 16

typedef struct {
    uint8_t kind;         /* CompKind */
    uint8_t na, nb;        /* electrical nodes, fixed per template */
    uint8_t ctrl;           /* controlling element index (dependent sources), 0xFF = n/a */
    uint8_t ctrl_a, ctrl_b;  /* controlling node pair when ctrl==0xFF and kind is dependent */
    uint8_t flags;            /* bit0 = polarity/direction flipped (editable, RAM-only) */
    uint8_t reg;               /* which draw-op register this is (== own index normally) */
    float value;                /* magnitude, editable (RAM-only). For CK_CAP/CK_IND this
                                   is the PHYSICAL value (farads/henries) - the reactance
                                   is derived from omega at solve time, which is what lets
                                   frequency be edited independently. */
    float deflt;                  /* template default, restores on (re)load */
    float value_im;                 /* phasor "j" part, editable; 0 for every DC circuit */
    float deflt_im;                   /* its template default */
} EditComp;
/* Shared editor operation: physical values are SI, including nF/pF. */
void edit_comp_set_magnitude(EditComp *c, float value);

/* Builds a plain-resistive-DC MnaTopology from the current (edited) values
 * of a component set, applying the flags-bit0 sign flip. `skip_kind_mask`
 * lets a caller omit e.g. capacitors (bit 1<<CK_CAP) for a steady-state
 * solve, or force one component's value to 0 for a deactivate/short. */
void build_mna(const EditComp *comps, uint8_t n, uint32_t skip_kind_mask,
               MnaTopology *out, uint8_t *elem_of_comp);

/* Phasor-domain build: same as build_mna(), but stamps CK_CAP/CK_IND as real
 * reactive elements at `omega` (rad/s) instead of collapsing them to
 * resistors, and carries each component's imaginary part through. Passing
 * omega == 0 is identical to calling build_mna(). */
void build_mna_ac(const EditComp *comps, uint8_t n, double omega,
                  MnaTopology *out, uint8_t *elem_of_comp);

/* ---- Narration output (no sprintf; see src/fmt.h) ----------------------- */
#define NARRATE_MAXLINES 64
#define NARRATE_LINEWIDTH 40

typedef struct {
    char text[NARRATE_LINEWIDTH];
    uint8_t color; /* COL_* from cv3.h - engine.c doesn't include cv3.h, caller maps if needed */
} NStep;

typedef struct {
    NStep steps[NARRATE_MAXLINES];
    uint8_t count;
    bool impossible;
    char impossible_reason[NARRATE_LINEWIDTH];
} Narration;

typedef struct { uint8_t elem; int8_t sign; } MeshEdge;

/* ---- Content routing --------------------------------------------------- */
/* Which narrator a template+exercise pair should run through. Order here
 * is also used as the bit index into a template's capability mask (which
 * OTHER contents could also legitimately solve this circuit - the
 * cross-content-listing feature), so keep it stable once content is
 * migrated. STATIC remains reserved for entries with no valid live route. */
typedef enum {
    CID_IMPEDANCIA_AC = 0,
    CID_NODAL_AC,
    CID_MALHAS_AC,
    CID_SUPERPOSICAO_AC,
    CID_THEVENIN_AC,
    CID_POTENCIA_AC,
    CID_MAX_POTENCIA_AC,
    CID_TRIFASICO,
    CID_CIRCUITOS_CH9,
    CID_COUNT,
    CID_STATIC = 0xFF
} ContentId;

#define CAP_BIT(cid) (1UL << (cid))

/* Implemented in src/appvar.c: live editing of the CURRENTLY LOADED
 * exercise's components (see exercise_load() in cv3.h). Mutate the
 * returned pointer's .value/.flags directly, then call
 * exercise_apply_edit() to recompute+repaginate the Resolucao/Resultado
 * pages (the Circuito page redraws live on its own, no separate call
 * needed - av_draw_circuit reads the same component array every draw). */
uint8_t exercise_comp_count(void);
EditComp *exercise_comp(uint8_t idx);
bool exercise_is_ac(void);
float exercise_frequency(void);
void exercise_set_frequency(float omega);
uint8_t exercise_param_count(void);
float exercise_param(uint8_t idx);
const char *exercise_param_name(uint8_t idx);
void exercise_set_param(uint8_t idx, float value);
void exercise_apply_edit(void);

/* line-builder: append pieces into one NStep, then commit it */
typedef struct { char buf[NARRATE_LINEWIDTH]; uint8_t pos; } LineBuf;
void lb_reset(LineBuf *lb);
void lb_str(LineBuf *lb, const char *s);
void lb_eng(LineBuf *lb, double v, const char *unit);
void lb_num(LineBuf *lb, double v);
void narrate_commit(Narration *n, uint8_t color, LineBuf *lb);
void narrate_reset(Narration *n);
bool narrate_mark_impossible(Narration *n, const char *reason);

#endif
