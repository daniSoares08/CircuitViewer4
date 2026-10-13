/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */

#include "engine.h"
#include "fmt.h"
#include <string.h>
#include <math.h>

void edit_comp_set_magnitude(EditComp *c, float value) {
    if (!isfinite(value)) return;
    switch(c->kind) {
    case CK_Z:case CK_VSRC:case CK_ISRC:case CK_DVS:case CK_DIS: {
        double angle=atan2(c->value_im,c->value);
        c->value=(float)(value*cos(angle));
        c->value_im=(float)(value*sin(angle));
        break;
    }
    default:
        c->value=value;
        c->flags=(uint8_t)(c->flags & 0xFE);
        break;
    }
}

void build_mna(const EditComp *comps, uint8_t n, uint32_t skip_kind_mask,
               MnaTopology *out, uint8_t *elem_of_comp) {
    uint8_t i, m;

    m = 0;
    for (i = 0; i < n; i++) {
        bool skip = comps[i].kind == CK_ARROW ||
                    (skip_kind_mask & (1UL << comps[i].kind)) != 0;
        elem_of_comp[i] = skip ? (uint8_t)0xFF : m++;
    }

    m = 0;
    for (i = 0; i < n; i++) {
        const EditComp *c = &comps[i];
        MnaElem *e;
        double v;

        if (elem_of_comp[i] == 0xFF) continue;
        e = &out->elems[m++];
        v = (c->flags & 1) ? -(double)c->value : (double)c->value;

        switch (c->kind) {
        case CK_RES: case CK_CAP: case CK_IND: e->kind = EK_R; break;
        case CK_VSRC: e->kind = EK_VSRC; break;
        case CK_ISRC: e->kind = EK_ISRC; break;
        case CK_DVS: e->kind = (uint8_t)((c->ctrl != 0xFF) ? EK_CCVS : EK_VCVS); break;
        case CK_DIS: e->kind = (uint8_t)((c->ctrl != 0xFF) ? EK_CCCS : EK_VCCS); break;
        default: e->kind = EK_R; break;
        }
        e->na = c->na;
        e->nb = c->nb;
        e->ctrl = (c->ctrl == 0xFF) ? (uint8_t)0xFF : elem_of_comp[c->ctrl];
        e->ctrl_a = c->ctrl_a;
        e->ctrl_b = c->ctrl_b;
        e->value = v;
        e->value_im = 0.0;
    }
    out->n_elems = m;
    out->omega = 0.0;   /* DC: selects the original real solver path */
}

void build_mna_ac(const EditComp *comps, uint8_t n, double omega,
                  MnaTopology *out, uint8_t *elem_of_comp) {
    uint8_t i, m;

    if (omega == 0.0) {
        build_mna(comps, n, 0, out, elem_of_comp);
        for(i=0;i<n;i++) {
            if(elem_of_comp[i]==0xFF)continue;
            if(comps[i].kind==CK_CAP) {
                out->elems[elem_of_comp[i]].kind=EK_ISRC;
                out->elems[elem_of_comp[i]].value=0;
            } else if(comps[i].kind==CK_IND ||
                     ((comps[i].kind==CK_RES || comps[i].kind==CK_Z) &&
                      comps[i].value==0 && comps[i].value_im==0)) {
                out->elems[elem_of_comp[i]].kind=EK_VSRC;
                out->elems[elem_of_comp[i]].value=0;
            }
        }
        return;
    }

    m = 0;
    for (i = 0; i < n; i++) {
        elem_of_comp[i] = (comps[i].kind == CK_ARROW) ? (uint8_t)0xFF : m++;
    }

    m = 0;
    for (i = 0; i < n; i++) {
        const EditComp *c = &comps[i];
        MnaElem *e;
        bool flip;

        if (elem_of_comp[i] == 0xFF) continue;
        e = &out->elems[m++];
        flip = (c->flags & 1) != 0;

        switch (c->kind) {
        case CK_RES: e->kind = EK_R; break;
        /* Reactive elements keep their PHYSICAL value; mna.c derives
         * Y = jwC / -j/(wL) at stamp time from the topology's omega. */
        case CK_CAP: e->kind = EK_C; break;
        case CK_IND: e->kind = EK_L; break;
        case CK_Z: e->kind = EK_Z; break;
        case CK_VSRC: e->kind = EK_VSRC; break;
        case CK_ISRC: e->kind = EK_ISRC; break;
        case CK_DVS: e->kind = (uint8_t)((c->ctrl != 0xFF) ? EK_CCVS : EK_VCVS); break;
        case CK_DIS: e->kind = (uint8_t)((c->ctrl != 0xFF) ? EK_CCCS : EK_VCCS); break;
        default: e->kind = EK_R; break;
        }
        e->na = c->na;
        e->nb = c->nb;
        e->ctrl = (c->ctrl == 0xFF) ? (uint8_t)0xFF : elem_of_comp[c->ctrl];
        e->ctrl_a = c->ctrl_a;
        e->ctrl_b = c->ctrl_b;
        if((c->kind==CK_RES || c->kind==CK_IND || c->kind==CK_Z) &&
                c->value==0 && c->value_im==0)e->kind=EK_VSRC;
        /* A polarity/direction flip negates the whole phasor, both parts -
         * flipping only the real part would rotate the angle instead of
         * reversing it. Impedances are never flipped (R/L/C ignore flags). */
        if (c->kind == CK_RES || c->kind == CK_CAP || c->kind == CK_IND) {
            e->value = c->value;
            e->value_im = 0.0;
        } else {
            e->value = flip ? -(double)c->value : (double)c->value;
            e->value_im = flip ? -(double)c->value_im : (double)c->value_im;
        }
    }
    out->n_elems = m;
    out->omega = omega;
}

/* ---- line builder -------------------------------------------------- */

void lb_reset(LineBuf *lb) {
    lb->pos = 0;
    lb->buf[0] = '\0';
}

void lb_str(LineBuf *lb, const char *s) {
    while (*s && lb->pos < NARRATE_LINEWIDTH - 1) lb->buf[lb->pos++] = *s++;
    lb->buf[lb->pos] = '\0';
}

void lb_eng(LineBuf *lb, double v, const char *unit) {
    char tmp[24];
    fmt_eng(tmp, v, unit);
    lb_str(lb, tmp);
}

void lb_num(LineBuf *lb, double v) {
    char tmp[24];
    fmt_num(tmp, v);
    lb_str(lb, tmp);
}

void narrate_reset(Narration *n) {
    n->count = 0;
    n->impossible = false;
    n->impossible_reason[0] = '\0';
}

void narrate_commit(Narration *n, uint8_t color, LineBuf *lb) {
    if (n->count >= NARRATE_MAXLINES) return;
    strncpy(n->steps[n->count].text, lb->buf, NARRATE_LINEWIDTH - 1);
    n->steps[n->count].text[NARRATE_LINEWIDTH - 1] = '\0';
    n->steps[n->count].color = color;
    n->count++;
    lb_reset(lb);
}

bool narrate_mark_impossible(Narration *n, const char *reason) {
    n->impossible = true;
    strncpy(n->impossible_reason, reason, NARRATE_LINEWIDTH - 1);
    n->impossible_reason[NARRATE_LINEWIDTH - 1] = '\0';
    return false;
}
