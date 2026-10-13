/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */

/* CV4DATA AppVar v2 loader - see .ai-tasks/spec_appvar_v2.md. Templates
 * (topology+draw-ops+reduction/mesh programs) and exercises (title,
 * statement text, template ref + value/flag overrides, content id) live in
 * archived AppVars read straight from Flash; only the CURRENT exercise's
 * live component values and the current page text get materialized into
 * RAM, mirroring CircuitViewer3's appvar.c (see [[circvie3-generator]]
 * memory for the "op interpreter reads straight from the flash pointer,
 * never copies the ops array" pattern this preserves). */

#include "cv3.h"
#include "engine.h"
#include "narrate.h"
#include "narrate_ac.h"
#include "narrate_power.h"
#include "fmt.h"
#include "live_recipe.h"
#include <fileioc.h>
#include <string.h>
#include <math.h>

#define AV_MAXC 8
#define AV_MAXP 32
#define AV_MAXL 8
#define AV_MAXMESH 6
#define AV_MAXMESHEDGE 6
#define MAX_TEXT_LINES 7
#define TEXT_X 14 /* matches tools/generate_cv4.py's TEXT_X exactly */
static const int16_t TEXT_YS[MAX_TEXT_LINES] = { 62, 82, 102, 122, 142, 162, 182 };

static const uint8_t *chunk_base[AV_MAXC];
static uint16_t chunk_tcount[AV_MAXC];
static uint16_t chunk_ecount[AV_MAXC];
static bool av_ok = false;
static uint16_t ru16(const uint8_t *p);
static float rf32(const uint8_t *p);

/* Validate all Flash blocks before any unbounded parser/string walk. A wrong
   revision, truncated transfer or corrupt offset must never become a RAM
   reset on ENTER. Readers below are only called on these checked blocks. */
static bool checked_bytes(const uint8_t **p,const uint8_t *end,uint16_t n) {
    if (*p>end || (size_t)(end-*p)<n) return false;
    *p+=n;return true;
}
static bool checked_string(const uint8_t **p,const uint8_t *end,uint8_t maxlen) {
    const uint8_t *q;
    if(*p>=end)return false;
    q=memchr(*p,0,(size_t)(end-*p));
    if(!q || (size_t)(q-*p)>maxlen)return false;
    *p=q+1;return true;
}
static bool checked_page(const uint8_t **p,const uint8_t *end) {
    uint8_t i,n;
    if(!checked_string(p,end,63)||!checked_string(p,end,63)||
       !checked_string(p,end,39)||!checked_bytes(p,end,2))return false;
    n=(*p)[-1];if(n>AV_MAXL)return false;
    for(i=0;i<n;i++)if(!checked_bytes(p,end,5)||!checked_string(p,end,39))return false;
    return true;
}
static bool checked_template(const uint8_t *p,const uint8_t *end) {
    uint8_t n,nodes,i,j,count;
    if(!checked_bytes(&p,end,6))return false;
    nodes=p[-6];n=p[-1];
    if(n>COMP_MAXN || nodes>MNA_MAXNODES || (n && !nodes) ||
       !isfinite(rf32(p-5)) || rf32(p-5)<0)return false;
    for(i=0;i<n;i++) {
        const uint8_t *c=p;
        if(!checked_bytes(&p,end,15))return false;
        if(c[0]>CK_Z || c[1]>=nodes || c[2]>=nodes ||
           (c[3]!=255 && c[3]>=n) || c[4]>=nodes || c[5]>=nodes ||
           !isfinite(rf32(c+6)) || !isfinite(rf32(c+10)))return false;
    }
    if(!checked_bytes(&p,end,1))return false;
    count=p[-1];
    for(i=0;i<count;i++) {
        if(!checked_bytes(&p,end,11) || (p[-1]!=255 && p[-1]>=n) ||
           !checked_string(&p,end,63))return false;
    }
    if(!checked_bytes(&p,end,1))return false;
    count=p[-1];if(count>AV_MAXMESH)return false;
    for(i=0;i<count;i++) {
        if(!checked_bytes(&p,end,1))return false;
        j=p[-1];if(j>AV_MAXMESHEDGE)return false;
        while(j--) {if(!checked_bytes(&p,end,2)||p[-2]>=n)return false;}
    }
    if(!checked_bytes(&p,end,3))return false;
    return p==end && (p[-3]==255 || p[-3]<nodes) && (p[-2]==255 || p[-2]<nodes);
}
static bool checked_exercise(const uint8_t *base,uint16_t nt,const uint8_t *p,const uint8_t *end) {
    uint16_t tid,len;uint8_t n=0,i,count;
    if(!checked_bytes(&p,end,5))return false;
    tid=ru16(p-5);
    if(tid!=65535) {
        if(tid>=nt)return false;
        n=base[ru16(base+8+2*tid)+5];
    }
    if(!checked_bytes(&p,end,1))return false;
    count=p[-1];
    for(i=0;i<count;i++)if(!checked_bytes(&p,end,9)||p[-9]>=n||
        !isfinite(rf32(p-8))||!isfinite(rf32(p-4)))return false;
    if(!checked_bytes(&p,end,1))return false;
    count=p[-1];
    for(i=0;i<count;i++)if(!checked_bytes(&p,end,2)||p[-2]>=n)return false;
    if(!checked_bytes(&p,end,2))return false;
    count=p[-1];if(count>64)return false;
    for(i=0;i<count;i++)if(!checked_bytes(&p,end,4)||!isfinite(rf32(p-4))||!checked_string(&p,end,12))return false;
    if(!checked_string(&p,end,63)||!checked_bytes(&p,end,1))return false;
    count=p[-1];if(count>4)return false;
    for(i=0;i<count;i++)if(!checked_page(&p,end))return false;
    if(!checked_bytes(&p,end,1))return false;
    count=p[-1];if(count)return false; /* no frozen answer tail in v2r3 */
    if(!checked_bytes(&p,end,2))return false;
    len=ru16(p-2);
    return checked_bytes(&p,end,len) && p==end;
}
static bool checked_chunk(const uint8_t *b,uint16_t size) {
    uint16_t nt,ne,table_end,k,off,next;const uint8_t *et;
    if(size<10 || memcmp(b,"CV4A\2\3",6))return false;
    nt=ru16(b+6);if(nt>(size-10)/2)return false;
    et=b+8+2*nt;ne=ru16(et);et+=2;
    if(ne>(size-10-2*nt)/2)return false;
    table_end=10+2*nt+2*ne;
    if(!ne || (nt?ru16(b+8):ru16(et))!=table_end)return false;
    for(k=0;k<nt;k++) {
        off=ru16(b+8+2*k);next=k+1<nt?ru16(b+10+2*k):ru16(et);
        if(off<table_end || next<=off || next>size || !checked_template(b+off,b+next))return false;
    }
    for(k=0;k<ne;k++) {
        off=ru16(et+2*k);next=k+1<ne?ru16(et+2*k+2):size;
        if(off<table_end || next<=off || next>size || !checked_exercise(b,nt,b+off,b+next))return false;
    }
    return true;
}

static Exercise m_ex;
static PageTemplate m_pages[AV_MAXP];
static TextLine m_lines[AV_MAXP][AV_MAXL];
static uint8_t m_n_pages;

static const uint8_t *m_circuit_ops; /* points into Flash; NULL = no circuit */
static uint8_t m_circuit_opn;

static EditComp m_comps[COMP_MAXN];
static uint8_t m_n_comps, m_n_nodes;
static uint8_t m_content_id, m_port_a, m_port_b, m_target;
static uint8_t m_resolution_start_slot;
static float m_params[64];
static const char *m_param_names[64];
static const uint8_t *m_live_program;
static uint16_t m_live_size;
static uint8_t m_n_params;
static uint8_t m_current_page;
static uint8_t m_params_start_slot;
static uint8_t m_params_page_count;
static uint8_t m_flags2;
static float m_omega;   /* rad/s for this template; 0 = DC */

static MeshEdge m_mesh_edges[AV_MAXMESH][AV_MAXMESHEDGE];
static uint8_t m_mesh_len[AV_MAXMESH];
static const MeshEdge *m_mesh_ptrs[AV_MAXMESH];
static uint8_t m_n_meshes;

/* ---- little-endian readers (mirror CircuitViewer3/src/appvar.c) -------- */

static uint16_t ru16(const uint8_t *p) { return (uint16_t)(p[0] | (p[1] << 8)); }
static int16_t ri16(const uint8_t *p) { return (int16_t)(p[0] | (p[1] << 8)); }

static float rf32(const uint8_t *p) {
    union { uint32_t u; float f; } v;
    v.u = (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
          ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
    return v.f;
}

static const char *rcstr(const uint8_t **pp) {
    const char *s = (const char *)*pp;
    *pp += strlen(s) + 1;
    return s;
}

void appvar_init(void) {
    uint8_t i;
    av_ok = false;
    for (i = 0; i < AV_MAXC; i++) {
        chunk_base[i] = NULL;
        chunk_tcount[i] = 0;
        chunk_ecount[i] = 0;
    }
    if (chunk_count > AV_MAXC) return;
    for (i = 0; i < chunk_count; i++) {
        char name[8] = "CV4DAT0";
        uint8_t f;
        const uint8_t *base;
        size_t size;
        name[6] = (char)('0' + i);
        f = ti_Open(name, "r");
        if (!f) return;
        base = (const uint8_t *)ti_GetDataPtr(f);
        size=ti_GetSize(f);
        ti_Close(f);
        if (!base || size>65535 || !checked_chunk(base,(uint16_t)size)) {
            return;
        }
        chunk_base[i] = base;
        chunk_tcount[i] = ru16(base + 6);
        chunk_ecount[i] = ru16(base + 8 + 2 * chunk_tcount[i]);
    }
    av_ok = true;
}

bool appvar_available(void) { return av_ok; }

void exercise_set_page(uint8_t page) {
    /* Pages materialize eagerly, but live parameter pages use the current
       slot to select their seven-value window. */
    m_current_page = page;
}

/* ---- template block --------------------------------------------------- */

static const uint8_t *template_offset_table(uint8_t chunk) {
    return chunk_base[chunk] + 8;
}

static bool template_load(uint8_t chunk, uint16_t local) {
    const uint8_t *base = chunk_base[chunk];
    const uint8_t *p;
    uint8_t i;

    if (!base || local >= chunk_tcount[chunk]) return false;
    p = base + ru16(template_offset_table(chunk) + 2 * local);

    m_n_nodes = *p++;
    m_omega = rf32(p); p += 4;   /* 0 = DC, nonzero = phasor domain */
    m_n_comps = *p++;
    if (m_n_comps > COMP_MAXN) m_n_comps = COMP_MAXN;
    {
        uint8_t stored_n = p[-1];
        for (i = 0; i < stored_n; i++) {
            EditComp c;
            c.kind = p[0];
            c.na = p[1];
            c.nb = p[2];
            c.ctrl = p[3];
            c.ctrl_a = p[4];
            c.ctrl_b = p[5];
            c.deflt = rf32(p + 6);
            c.deflt_im = rf32(p + 10);
            c.flags = p[14];
            c.value = c.deflt;
            c.value_im = c.deflt_im;
            c.reg = i;
            p += 15;
            if (i < COMP_MAXN) m_comps[i] = c;
        }
    }

    {
        uint8_t n_ops = *p++;
        m_circuit_ops = n_ops ? p : NULL;
        m_circuit_opn = n_ops;
        for (i = 0; i < n_ops; i++) {
            p += 10; /* opcode(1)+a,b,c,d(8)+flag(1) */
            p++;     /* reg */
            p += strlen((const char *)p) + 1; /* label cstr */
        }
    }

    {
        uint8_t n_meshes = *p++;
        uint8_t mi, ei;
        m_n_meshes = (n_meshes > AV_MAXMESH) ? AV_MAXMESH : n_meshes;
        for (mi = 0; mi < n_meshes; mi++) {
            uint8_t ec = *p++;
            for (ei = 0; ei < ec; ei++) {
                if (mi < AV_MAXMESH && ei < AV_MAXMESHEDGE) {
                    m_mesh_edges[mi][ei].elem = p[0];
                    m_mesh_edges[mi][ei].sign = (int8_t)p[1];
                }
                p += 2;
            }
            if (mi < AV_MAXMESH) {
                m_mesh_len[mi] = (ec > AV_MAXMESHEDGE) ? AV_MAXMESHEDGE : ec;
                m_mesh_ptrs[mi] = m_mesh_edges[mi];
            }
        }
    }

    m_port_a = *p++;
    m_port_b = *p++;
    m_flags2 = *p++;
    return true;
}

/* ---- page-block reader for the original statement --------------------- */

static const uint8_t *read_page_block(const uint8_t *p, uint8_t slot) {
    const char *title = rcstr(&p);
    const char *sub = rcstr(&p);
    const char *res = rcstr(&p);
    uint8_t ry = *p++;
    uint8_t lc = *p++;
    uint8_t li;

    for (li = 0; li < lc; li++) {
        int16_t x = ri16(p); p += 2;
        int16_t y = ri16(p); p += 2;
        uint8_t col = *p++;
        const char *t = rcstr(&p);
        if (li < AV_MAXL) {
            m_lines[slot][li].text = t;
            m_lines[slot][li].x = x;
            m_lines[slot][li].y = y;
            m_lines[slot][li].color = col;
        }
    }
    m_pages[slot].title = title;
    m_pages[slot].subtitle = sub;
    m_pages[slot].lines = m_lines[slot];
    m_pages[slot].line_count = (lc > AV_MAXL) ? AV_MAXL : lc;
    m_pages[slot].result = res[0] ? res : 0;
    m_pages[slot].result_y = ry;
    m_pages[slot].body = 0;
    return p;
}

/* ---- circuit drawing: live labels from m_comps[], live polarity/dir ---- */

/* Compact single-token unit shown after an EDITED component value. Resistors
 * are bare (they sit inside a narrow box; "ohm" would overflow and collide
 * with neighbours). Dependent-source gains are also bare because their unit
 * depends on the controller type. */
static const char *edit_suffix_for_kind(uint8_t kind) {
    switch (kind) {
    case CK_VSRC: return "V";
    case CK_ISRC: return "A";
    case CK_CAP: return "F";
    case CK_IND: return "H";
    case CK_Z: return "ohm";
    default: return ""; /* resistor: bare number */
    }
}

/* Label shown for a component register: the ORIGINAL authored string while
 * the value is untouched (identical to v3, correct implicit unit, fits),
 * else a compact reformat of the live value. This includes dependent-source
 * gains: an edited value must never leave the old numeric label on screen. */
static const char *reg_label(uint8_t reg, const char *stored, char *scratch) {
    uint8_t kind = m_comps[reg].kind;
    if (m_comps[reg].value == m_comps[reg].deflt &&
        m_comps[reg].value_im == m_comps[reg].deflt_im) return stored;
    if (kind==CK_Z) {
        fmt_rect_label(scratch,m_comps[reg].value,m_comps[reg].value_im);
        return scratch;
    }
    if (((kind == CK_VSRC || kind == CK_ISRC ||
                           kind == CK_DVS || kind == CK_DIS)) &&
                         m_comps[reg].value_im != 0.0f) {
        fmt_polar_label(scratch, (double)m_comps[reg].value,
                  (double)m_comps[reg].value_im, edit_suffix_for_kind(kind));
        return scratch;
    }
    fmt_label(scratch, (double)m_comps[reg].value, edit_suffix_for_kind(kind));
    if (kind==CK_DVS || kind==CK_DIS) {
        const char *p=stored;
        uint8_t n=(uint8_t)strlen(scratch);
        while ((*p>='0'&&*p<='9')||*p=='.'||*p=='+'||*p=='-') ++p;
        if (*p=='k'||*p=='m'||*p=='u'||*p=='n'||*p=='p') ++p;
        while (*p && n<31) scratch[n++]=*p++;
        scratch[n]=0;
    }
    return scratch;
}

/* flags2 bit3: algebraic phasor Acos*cos(wt)+Asin*sin(wt).
 * This diagram is rebuilt from current parameters, never frozen geometry.
 * A rectangular fit keeps every quadrant inside the circuit body area. */
static void av_draw_phasor(void) {
    float re, im, norm, dx, dy, len, ux, uy;
    int16_t x, y;
    if (m_n_params < 2) return;
    re=m_params[0]; im=-m_params[1];
    norm=fmaxf(fabsf(re)/86.0f,fabsf(im)/58.0f);
    if (norm==0.0f) { draw_node(160,136); return; }
    dx=re/norm; dy=-im/norm; x=(int16_t)(160+dx); y=(int16_t)(136+dy);
    len=sqrtf(dx*dx+dy*dy); ux=dx/len; uy=dy/len;
    draw_wire(160,136,x,y);
    draw_wire(x,y,(int16_t)(x-8*ux+4*uy),(int16_t)(y-8*uy-4*ux));
    draw_wire(x,y,(int16_t)(x-8*ux-4*uy),(int16_t)(y-8*uy+4*ux));
}

static void av_draw_circuit(void) {
    const uint8_t *p = m_circuit_ops;
    uint8_t n = m_circuit_opn;
    uint8_t i;
    char labbuf[32];

    if (!p) return;
    for (i = 0; i < n; i++) {
        uint8_t op = *p++;
        int16_t a = ri16(p); p += 2;
        int16_t b = ri16(p); p += 2;
        int16_t c = ri16(p); p += 2;
        int16_t d = ri16(p); p += 2;
        uint8_t fl = *p++;
        uint8_t reg = *p++;
        const char *stored = rcstr(&p);
        const char *lab = stored;
        bool has_reg = reg != 0xFF && reg < m_n_comps;
        bool flipped = has_reg && (m_comps[reg].flags & 1) != 0;
        /* flags bit0 flips the AUTHORED default direction/polarity in fl.
         * It never sets an absolute state: it only inverts the template
         * default, including voltage-source polarity. */
        bool dir = flipped ? !fl : (fl ? true : false);

        if (has_reg && m_comps[reg].kind != CK_ARROW) {
            lab = reg_label(reg, stored, labbuf);
        }

        switch (op) {
        case 0:  draw_wire(a, b, c, d); break;
        case 1:  draw_node(a, b); break;
        case 2:  draw_terminal(a, b, lab); break;
        case 3:  draw_res_h(a, b, c, lab); break;
        case 4:  draw_res_v(a, b, c, lab); break;
        case 5:  draw_cap_h(a, b, c, lab); break;
        case 6:  draw_cap_v(a, b, c, lab); break;
        case 7:  draw_ind_h(a, b, c, lab); break;
        case 8:  draw_ind_v(a, b, c, lab); break;
        case 9:  draw_voltage_source_pol(a, b, c, lab, dir); break;
        case 10: draw_voltage_source_h_pol(a, b, c, lab, dir); break;
        case 11: draw_current_source_v_dir(a, b, c, lab, dir); break;
        case 12: draw_current_source_h_dir(a, b, c, lab, dir); break;
        case 13: draw_ground(a, b); break;
        case 14: draw_switch_open_h(a, b, c, lab); break;
        case 15: draw_opamp(a, b, fl ? true : false); break;
        case 16: draw_dep_vsource_v_pol(a, b, c, lab, dir); break;
        case 17: draw_dep_vsource_h_pol(a, b, c, lab, dir); break;
        case 18: draw_dep_isource_v(a, b, c, lab, dir); break;
        case 19: ui_label(lab, a, b); break;
        case 20: ui_arrow_h(a, b, c, lab, dir); break;
        case 21: ui_arrow_v(a, b, c, lab, dir); break;
        case 22: ui_vo(a, b, c, lab); break;
        case 23: ui_pm(a, b, c); break;
        case 24: draw_res_h(a, b, c, lab); break;
        case 25: draw_res_v(a, b, c, lab); break;
        default: break;
        }
    }
    if (m_flags2 & 8) av_draw_phasor();
}

/* Scalar givens that do not map to a drawn electrical component still need
 * the same honest edit loop.  This live page prevents a static textbook
 * statement from appearing to contain the edited value: after MODE edits,
 * these are the authoritative current values held in RAM. */
static void av_draw_params(void) {
    uint8_t page_index, first, last, i;
    char line[40], value[20];

    if (!m_params_page_count || m_current_page < m_params_start_slot) return;
    page_index = (uint8_t)(m_current_page - m_params_start_slot);
    if (page_index >= m_params_page_count) return;
    first = (uint8_t)(page_index * 7);
    last = (uint8_t)(first + 7);
    if (last > m_n_params) last = m_n_params;

    for (i = first; i < last; i++) {
        strcpy(line, m_param_names[i]);
        strcat(line, " = ");
        fmt_eng(value, m_params[i], "");
        strcat(line, value);
        prn(line, TEXT_X, TEXT_YS[i - first]);
    }
}

/* ---- dynamic Resolucao/Resultado (re)generation ------------------------ */

static const char *node_label_of[MNA_MAXNODES];

static uint8_t paginate(const Narration *n, uint8_t start_slot, uint8_t max_slot) {
    uint8_t slot = start_slot;
    uint8_t i = 0;

    if (n->impossible) {
        m_pages[slot].title = "Resolucao";
        m_pages[slot].subtitle = "impossivel";
        m_lines[slot][0].text = "IMPOSSIVEL por este metodo:";
        m_lines[slot][0].x = TEXT_X; m_lines[slot][0].y = TEXT_YS[0]; m_lines[slot][0].color = COL_RED;
        m_lines[slot][1].text = n->impossible_reason;
        m_lines[slot][1].x = TEXT_X; m_lines[slot][1].y = TEXT_YS[1]; m_lines[slot][1].color = COL_BLACK;
        m_pages[slot].lines = m_lines[slot];
        m_pages[slot].line_count = 2;
        m_pages[slot].result = 0;
        m_pages[slot].body = 0;
        return (uint8_t)(slot + 1);
    }

    while (i < n->count && slot < max_slot) {
        uint8_t li = 0;
        uint8_t remaining_lines = (uint8_t)(n->count - i);
        uint8_t this_page_lines = remaining_lines > MAX_TEXT_LINES ? MAX_TEXT_LINES : remaining_lines;
        bool is_last_group = (uint8_t)(i + this_page_lines) >= n->count;

        m_pages[slot].title = "Resolucao";
        m_pages[slot].subtitle = "passo a passo";
        while (li < this_page_lines) {
            m_lines[slot][li].text = n->steps[i].text;
            m_lines[slot][li].x = TEXT_X;
            m_lines[slot][li].y = TEXT_YS[li];
            m_lines[slot][li].color = n->steps[i].color;
            li++;
            i++;
        }
        m_pages[slot].lines = m_lines[slot];
        m_pages[slot].line_count = li;
        m_pages[slot].result = 0;
        m_pages[slot].body = 0;
        (void)is_last_group;
        slot++;
    }
    return slot;
}

static uint8_t build_result_pages(const Narration *n, uint8_t slot) {
    uint8_t i=0,li=0;
    do {
        m_pages[slot].title="Resultados atuais";
        m_pages[slot].subtitle=n->impossible?"Confira os dados":"Valores recalculados";
        m_pages[slot].lines=m_lines[slot];m_pages[slot].body=0;
        m_pages[slot].result=0;m_pages[slot].result_y=0;li=0;
        if(n->impossible || !n->count) {
            m_lines[slot][li].text=n->impossible?n->impossible_reason:"Sem resultado calculado";
            m_lines[slot][li].x=TEXT_X;m_lines[slot][li].y=TEXT_YS[li];
            m_lines[slot][li++].color=COL_RED;i=n->count;
        }else {
            while(i<n->count && li<MAX_TEXT_LINES) {
                if(n->steps[i].color==NCOL_RED || (!m_live_size && i==n->count-1)) {
                    m_lines[slot][li].text=n->steps[i].text;
                    m_lines[slot][li].x=TEXT_X;m_lines[slot][li].y=TEXT_YS[li];
                    m_lines[slot][li++].color=COL_RED;
                }
                i++;
            }
        }
        m_pages[slot].line_count=li;slot++;
    }while(i<n->count && slot<AV_MAXP);
    return slot;
}

static void av_rebuild_resolution(uint8_t from_slot) {
    /* Narration is ~2.7 KiB. Keep it out of the small CE call stack; the
       impedance path nests a topology copy for the 1 A test source. */
    static Narration nar;
    uint8_t next;

    if (m_live_size) {
        LiveInputs inputs;
        inputs.comps=m_comps; inputs.n_comps=m_n_comps;
        inputs.n_nodes=m_n_nodes;inputs.params=m_params;
        inputs.n_params=m_n_params;inputs.omega=m_omega;
        if (!live_recipe_run(m_live_program,m_live_size,&inputs,&nar) && !nar.impossible)
            narrate_mark_impossible(&nar,"programa de calculo invalido");
        { uint8_t k,reds=0;
          for(k=0;k<nar.count;k++)if(nar.steps[k].color==NCOL_RED)reds++;
          next=paginate(&nar,from_slot,(uint8_t)(AV_MAXP-((reds+6)/7? (reds+6)/7:1)));
        }
        m_n_pages=build_result_pages(&nar,next);m_ex.page_count=m_n_pages;
        return;
    }

    switch (m_content_id) {
    case CID_NODAL_AC: {
        uint8_t k;
        for (k = 0; k < m_n_nodes && k < MNA_MAXNODES; k++) node_label_of[k] = 0;
        narrate_ac_nodal(m_comps, m_n_comps, m_n_nodes, (double)m_omega,
                         node_label_of, m_target, (m_flags2 & 2) != 0, &nar);
        break;
    }
    case CID_CIRCUITOS_CH9: {
        uint8_t k;
        for (k = 0; k < m_n_nodes && k < MNA_MAXNODES; k++) node_label_of[k] = 0;
        narrate_ac_nodal(m_comps, m_n_comps, m_n_nodes, (double)m_omega,
                         node_label_of, m_target, (m_flags2 & 2) != 0, &nar);
        break;
    }
    case CID_IMPEDANCIA_AC:
        narrate_ac_impedance(m_comps, m_n_comps, m_n_nodes, (double)m_omega,
                             m_port_a, m_port_b, &nar);
        break;
    case CID_MALHAS_AC:
        narrate_ac_mesh(m_comps, m_n_comps, m_n_nodes, (double)m_omega,
                        m_mesh_ptrs, m_mesh_len, m_n_meshes, m_target, &nar);
        break;
    case CID_SUPERPOSICAO_AC:
        narrate_ac_superposition(m_comps, m_n_comps, m_n_nodes, (double)m_omega,
                                 m_target, &nar);
        break;
    case CID_THEVENIN_AC:
        narrate_ac_thevenin(m_comps, m_n_comps, m_n_nodes, (double)m_omega,
                            m_port_a, m_port_b, &nar);
        break;
    case CID_POTENCIA_AC:
        if (!m_n_comps)
            narrate_power_profile(m_target, m_params, m_n_params, &nar);
        else if (m_target == 0xFF && m_port_a != 0xFF && m_port_b != 0xFF)
            narrate_ac_power_factor(m_comps, m_n_comps, m_n_nodes,
                                    (double)m_omega, m_port_a, m_port_b, &nar);
        else
            narrate_ac_power(m_comps, m_n_comps, m_n_nodes, (double)m_omega,
                             m_target, (m_flags2 & 1) != 0,
                             (m_flags2 & 4) != 0, &nar);
        break;
    case CID_MAX_POTENCIA_AC:
        if (m_n_comps)
            narrate_ac_max_power(m_comps, m_n_comps, m_n_nodes,
                                 (double)m_omega, m_port_a, m_port_b,
                                 (m_flags2 & 1) != 0, &nar);
        else
            narrate_max_power(m_params, m_n_params, &nar);
        break;
    case CID_TRIFASICO:
        if (m_target == 0xFF)
            narrate_three_phase(m_params, m_n_params, &nar);
        else
            narrate_three_phase_profile(m_target, m_params, m_n_params, &nar);
        break;
    default:
        narrate_reset(&nar);
        narrate_mark_impossible(&nar, "conteudo ainda nao implementado");
        break;
    }

    { uint8_t k,reds=0;
      for(k=0;k<nar.count;k++)if(nar.steps[k].color==NCOL_RED || k==nar.count-1)reds++;
      next=paginate(&nar,from_slot,(uint8_t)(AV_MAXP-((reds+6)/7? (reds+6)/7:1)));
    }
    m_n_pages = build_result_pages(&nar, next);
    m_ex.page_count = m_n_pages;
}

/* ---- exercise block ----------------------------------------------------- */

static const uint8_t *exercise_offset_table(uint8_t chunk) {
    const uint8_t *p = template_offset_table(chunk);
    p += 2 * chunk_tcount[chunk];
    p += 2; /* n_exercises u16 already consumed via chunk_ecount at init */
    return p;
}

const Exercise *exercise_load(uint16_t idx) {
    const ExMeta *meta;
    const uint8_t *base;
    const uint8_t *p;
    uint16_t template_id;
    uint8_t n_over, i, slot;
    static char title_buf[28];

    if (!av_ok || idx >= ex_count) return NULL;
    meta = &ex_meta[idx];
    if (meta->chunk >= chunk_count) return NULL;
    base = chunk_base[meta->chunk];
    if (!base || meta->local >= chunk_ecount[meta->chunk]) return NULL;
    p = base + ru16(exercise_offset_table(meta->chunk) + 2 * meta->local);

    template_id = ru16(p); p += 2;
    m_content_id = *p++;
    p += 2; /* chapter, section - menu ordering only, already baked into ex_meta placement */

    if (template_id != 0xFFFF) {
        if (!template_load(meta->chunk, template_id)) return NULL;
    } else {
        m_circuit_ops = NULL;
        m_circuit_opn = 0;
        m_n_comps = 0;
        m_n_nodes = 0;
        m_omega = 0.0f;
        m_port_a = m_port_b = 0xFF;
        m_flags2 = 0;
        m_n_meshes = 0;
    }

    n_over = *p++;
    for (i = 0; i < n_over; i++) {
        uint8_t ci = p[0];
        float v = rf32(p + 1);
        float vi = rf32(p + 5);
        p += 9;
        if (ci < m_n_comps) {
            m_comps[ci].value = m_comps[ci].deflt = v;
            m_comps[ci].value_im = m_comps[ci].deflt_im = vi;
        }
    }
    n_over = *p++;
    for (i = 0; i < n_over; i++) {
        uint8_t ci = p[0];
        uint8_t fl = p[1];
        p += 2;
        if (ci < m_n_comps) m_comps[ci].flags = fl;
    }
    m_target = *p++;
    m_n_params = *p++;
    m_current_page = 0;
    m_params_start_slot = 0xFF;
    m_params_page_count = 0;
    if (m_n_params > 64) return NULL;
    for (i = 0; i < m_n_params; i++) {
        m_params[i] = rf32(p); p += 4;
        m_param_names[i] = rcstr(&p);
    }

    {
        const char *t = rcstr(&p);
        uint8_t j = 0;
        while (t[j] && j < sizeof(title_buf) - 1) { title_buf[j] = t[j]; j++; }
        title_buf[j] = '\0';
    }

    slot = 0;
    if (m_circuit_opn > 0) {
        m_pages[slot].title = "Circuito";
        m_pages[slot].subtitle = "";
        m_pages[slot].lines = m_lines[slot];
        m_pages[slot].line_count = 0;
        m_pages[slot].result = 0;
        m_pages[slot].body = av_draw_circuit;
        slot++;
    }

    {
        uint8_t n_enun = *p++;
        for (i = 0; i < n_enun && slot < AV_MAXP; i++) {
            p = read_page_block(p, slot);
            m_pages[slot].title="Enunciado original";
            slot++;
        }
    }

    if (m_n_params && slot < AV_MAXP) {
        uint8_t param_page;
        m_params_start_slot = slot;
        m_params_page_count = (uint8_t)((m_n_params + 6) / 7);
        for (param_page = 0;
             param_page < m_params_page_count && slot < AV_MAXP;
             param_page++, slot++) {
            m_pages[slot].title = "Dados atuais";
            m_pages[slot].subtitle = "MODE para editar";
            m_pages[slot].lines = m_lines[slot];
            m_pages[slot].line_count = 0;
            m_pages[slot].result = 0;
            m_pages[slot].body = av_draw_params;
        }
    }

    m_resolution_start_slot = slot;
    m_live_size=0;m_live_program=NULL;
    {
        uint8_t n_tail = *p++;
        if (n_tail != 0) {
            for (i = 0; i < n_tail && slot < AV_MAXP; i++) {
                p = read_page_block(p, slot);
                slot++;
            }
            m_n_pages = slot;
            m_ex.page_count = m_n_pages;
        }
        m_live_size=ru16(p);p+=2;
        m_live_program=m_live_size?p:NULL;
        if(m_live_size || !n_tail)av_rebuild_resolution(m_resolution_start_slot);
    }

    m_ex.title = title_buf;
    m_ex.pages = m_pages;
    return &m_ex;
}

/* ---- live editing --------------------------------------------------- */

uint8_t exercise_comp_count(void) {
    return m_n_comps;
}
EditComp *exercise_comp(uint8_t idx) { return (idx < m_n_comps) ? &m_comps[idx] : 0; }
bool exercise_is_ac(void) {
    return m_n_comps && m_omega>0.0f;
}
float exercise_frequency(void) { return m_omega; }
void exercise_set_frequency(float omega) {
    if (omega > 0.0f) m_omega = omega;
    exercise_apply_edit();
}
uint8_t exercise_param_count(void) { return m_n_params; }
float exercise_param(uint8_t idx) { return idx < m_n_params ? m_params[idx] : 0.0f; }
const char *exercise_param_name(uint8_t idx) {
    return idx < m_n_params ? m_param_names[idx] : "?";
}
void exercise_set_param(uint8_t idx, float value) {
    if (idx < m_n_params) m_params[idx] = value;
    exercise_apply_edit();
}

void exercise_apply_edit(void) {
    /* Same calculation on first opening and every value/flag edit. Circuit
       drawing reads m_comps[] live; results and all steps are rebuilt here. */
    if (m_live_size || m_content_id != CID_STATIC) {
        av_rebuild_resolution(m_resolution_start_slot);
    }
}
