#include "live_recipe.h"
#include "fmt.h"
#include "narrate.h"
#include <math.h>
#include <string.h>

/* Bytecode contract is mirrored by tools/live_recipe.py. No dynamic allocation,
   recursion, source-text evaluation or calls back into the user interface. */
enum { L_CONST=1, L_PARAM, L_COMP, L_Z, L_NODE, L_CURRENT, L_POWER,
       L_VAR, L_OMEGA, L_VTH, L_ZTH,
       L_ADD=20, L_SUB, L_MUL, L_DIV, L_NEG, L_POW,
       L_ABS=30, L_ARG, L_REAL, L_IMAG, L_CONJ, L_SQRT,
       L_SIN, L_COS, L_TAN, L_ACOS, L_ATAN, L_EXP, L_LOG,
       L_POLAR, L_COMPLEX, L_MIN, L_MAX, L_CSQRT, L_SOLVE, L_GUARD,
       L_EQ, L_LT, L_LE, L_AND };
static LiveValue vars[LIVE_MAXVARS], stack[LIVE_STACK];
static uint8_t var_count;
static MnaTopology topo;
static MnaResult solved, test;
static uint8_t elem_map[COMP_MAXN];
static LiveValue vth, zth;
static const float PI_F=3.14159265358979323846f;
static uint8_t opamp_nodes[4][3], opamp_count, removed, port_a, port_b;
static bool solved_valid,port_valid;
static bool solve_network(const LiveInputs *in,float w,uint16_t mask,bool port) {
    uint8_t i;
    topo.n_nodes=in->n_nodes;
    build_mna_ac(in->comps,in->n_comps,w,&topo,elem_map);
    for(i=0;i<in->n_comps;i++) {
        MnaElem *e;
        if(elem_map[i]==0xFF)continue;
        e=&topo.elems[elem_map[i]];
        if(i==removed) {e->kind=EK_ISRC;e->value=e->value_im=0;}
        else if((in->comps[i].kind==CK_VSRC || in->comps[i].kind==CK_ISRC) && !(mask&(1u<<i)))
            e->value=e->value_im=0;
    }
    for(i=0;i<opamp_count;i++) {
        MnaElem *e;
        if(topo.n_elems>=MNA_MAXELEM)return false;
        e=&topo.elems[topo.n_elems++];memset(e,0,sizeof(*e));
        e->kind=EK_OPAMP;e->na=opamp_nodes[i][0];
        e->ctrl_a=opamp_nodes[i][1];e->ctrl_b=opamp_nodes[i][2];e->ctrl=0xFF;
    }
    solved_valid=port_valid=false;
    if(!mna_solve(&topo,&solved))return false;
    solved_valid=true;
    if(port) {
        if(port_a>=in->n_nodes || port_b>=in->n_nodes || port_a==port_b ||
           !mna_solve_test_source(&topo,port_a,port_b,&test))return false;
        vth.re=solved.node_v[port_a]-solved.node_v[port_b];
        vth.im=solved.node_v_im[port_a]-solved.node_v_im[port_b];
        zth.re=test.node_v[port_a]-test.node_v[port_b];
        zth.im=test.node_v_im[port_a]-test.node_v_im[port_b];
        port_valid=true;
    }
    return true;
}

static LiveValue val(float r, float i) { LiveValue v; v.re=r; v.im=i; return v; }
static LiveValue add(LiveValue a, LiveValue b) { return val(a.re+b.re,a.im+b.im); }
static LiveValue sub(LiveValue a, LiveValue b) { return val(a.re-b.re,a.im-b.im); }
static LiveValue mul(LiveValue a, LiveValue b) {
    return val(a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re);
}
static bool divide(LiveValue a, LiveValue b, LiveValue *r) {
    float scale=fmaxf(fabsf(b.re),fabsf(b.im)), den;
    if(scale==0 || !isfinite(scale)) return false;
    b.re/=scale; b.im/=scale; den=b.re*b.re+b.im*b.im;
    *r=val((a.re/scale*b.re+a.im/scale*b.im)/den,
           (a.im/scale*b.re-a.re/scale*b.im)/den);
    return isfinite(r->re) && isfinite(r->im);
}
static uint16_t u16(const uint8_t *p) { return (uint16_t)(p[0]|((uint16_t)p[1]<<8)); }
static float f32(const uint8_t *p) {
    union { uint32_t u; float f; } v;
    v.u=(uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
    return v.f;
}
static LiveValue comp_value(const EditComp *c) {
    float s=(c->flags&1)?-1.0f:1.0f;
    return val(s*c->value,s*c->value_im);
}
static bool impedance(const EditComp *c,float w,LiveValue *v) {
    if(c->kind==CK_CAP) {
        if(w==0 || c->value==0) return false;
        *v=val(0,-1/(w*c->value));
    } else if(c->kind==CK_IND) *v=val(0,w*c->value);
    else *v=val(c->value,c->value_im);
    return true;
}
static bool eval(const uint8_t *p,const uint8_t *end,const LiveInputs *in,LiveValue *out) {
    uint8_t sp=0;
    while(p<end) {
        uint8_t op=*p++, k;
        LiveValue a,b,r;
        if(op<L_ADD) {
            if(sp>=LIVE_STACK) return false;
            switch(op) {
            case L_CONST:
                if(end-p<4) return false;
                r=val(f32(p),0); p+=4; break;
            case L_OMEGA:r=val(in->omega,0); break;
            case L_VTH:if(!port_valid)return false;r=vth;break;
            case L_ZTH:if(!port_valid)return false;r=zth;break;
            default:
                if(p>=end) return false;
                k=*p++;
                switch(op) {
                case L_PARAM:if(k>=in->n_params)return false;r=val(in->params[k],0);break;
                case L_VAR:if(k>=var_count)return false;r=vars[k];break;
                case L_NODE:if(!solved_valid || k>=in->n_nodes)return false;r=val(solved.node_v[k],solved.node_v_im[k]);break;
                default:
                    if(k>=in->n_comps)return false;
                    if(op==L_COMP)r=comp_value(&in->comps[k]);
                    else if(op==L_Z){if(!impedance(&in->comps[k],in->omega,&r))return false;}
                    else if(op==L_CURRENT){if(!solved_valid || elem_map[k]==0xFF)return false;r=val(solved.elem_i[elem_map[k]],solved.elem_i_im[elem_map[k]]);}
                    else if(op==L_POWER){
                        const EditComp *c=&in->comps[k];
                        if(!solved_valid || elem_map[k]==0xFF)return false;
                        a=val(solved.node_v[c->na]-solved.node_v[c->nb],
                              solved.node_v_im[c->na]-solved.node_v_im[c->nb]);
                        b=val(solved.elem_i[elem_map[k]],-solved.elem_i_im[elem_map[k]]);
                        r=mul(a,b);
                    } else return false;
                }
            }
            if(!isfinite(r.re)||!isfinite(r.im))return false;
            stack[sp++]=r; continue;
        }
        if(sp==0)return false;
        a=stack[--sp];
        if(op==L_ADD||op==L_SUB||op==L_MUL||op==L_DIV||op==L_POW||
           op==L_POLAR||op==L_COMPLEX||op==L_MIN||op==L_MAX||op==L_SOLVE||
           op==L_EQ||op==L_LT||op==L_LE||op==L_AND) {
            if(sp==0)return false;
            b=a; a=stack[--sp];
        }
        switch(op) {
        case L_ADD:r=add(a,b);break;
        case L_SUB:r=sub(a,b);break;
        case L_MUL:r=mul(a,b);break;
        case L_DIV:if(!divide(a,b,&r))return false;break;
        case L_NEG:r=val(-a.re,-a.im);break;
        case L_ABS:r=val(hypotf(a.re,a.im),0);break;
        case L_ARG:r=val(atan2f(a.im,a.re)*180/PI_F,0);break;
        case L_REAL:r=val(a.re,0);break;
        case L_IMAG:r=val(a.im,0);break;
        case L_CONJ:r=val(a.re,-a.im);break;
        case L_SQRT:
            if(a.im!=0 || a.re<0)return false;
            r=val(sqrtf(a.re),0);break;
        case L_CSQRT: {
            float mag=hypotf(a.re,a.im);
            r=val(sqrtf(fmaxf(0,(mag+a.re)/2)),
                  (a.im<0?-1:1)*sqrtf(fmaxf(0,(mag-a.re)/2)));break;
        }
        case L_SIN:r=val(sinf(a.re*PI_F/180),0);break;
        case L_COS:r=val(cosf(a.re*PI_F/180),0);break;
        case L_TAN:r=val(tanf(a.re*PI_F/180),0);break;
        case L_ACOS:
            if(a.re < -1.000001f || a.re>1.000001f)return false;
            r=val(acosf(fmaxf(-1,fminf(1,a.re)))*180/PI_F,0);break;
        case L_ATAN:r=val(atanf(a.re)*180/PI_F,0);break;
        case L_EXP:r=val(expf(a.re),0);break;
        case L_LOG:if(a.re<=0)return false;r=val(logf(a.re),0);break;
        case L_POW:
            if(b.im!=0)return false;
            if(a.im==0 && (a.re>=0 || floorf(b.re)==b.re))r=val(powf(a.re,b.re),0);
            else {
                float mag=powf(hypotf(a.re,a.im),b.re),angle=atan2f(a.im,a.re)*b.re;
                r=val(mag*cosf(angle),mag*sinf(angle));
            }break;
        case L_POLAR:r=val(a.re*cosf(b.re*PI_F/180),a.re*sinf(b.re*PI_F/180));break;
        case L_COMPLEX:r=val(a.re,b.re);break;
        case L_MIN:r=val(fminf(a.re,b.re),0);break;
        case L_MAX:r=val(fmaxf(a.re,b.re),0);break;
        case L_SOLVE:
            if(a.im!=0 || a.re<0 || b.re<0 || b.re>65535 ||
               !solve_network(in,a.re,(uint16_t)b.re,false))return false;
            r=a;break;
        case L_GUARD:if(a.re==0 || a.im!=0)return false;r=a;break;
        case L_EQ:r=val(a.re==b.re && a.im==b.im,0);break;
        case L_LT:r=val(a.re<b.re,0);break;
        case L_LE:r=val(a.re<=b.re,0);break;
        case L_AND:r=val(a.re!=0 && b.re!=0,0);break;
        default:return false;
        }
        if(!isfinite(r.re)||!isfinite(r.im))return false;
        stack[sp++]=r;
    }
    if(sp!=1)return false;
    *out=stack[0];return true;
}
bool live_recipe_value(uint8_t index,LiveValue *out) {
    if(index>=var_count)return false;
    *out=vars[index];return true;
}
bool live_recipe_run(const uint8_t *program,uint16_t size,
                     const LiveInputs *in,Narration *out) {
    const uint8_t *p=program,*end=program+size;
    uint8_t flags, extras, i;
    LineBuf lb;
    narrate_reset(out);var_count=0;solved_valid=port_valid=false;
    if(in->n_comps>COMP_MAXN || in->n_nodes>MNA_MAXNODES || in->n_params>64 || !isfinite(in->omega))
        return narrate_mark_impossible(out,"dados de entrada invalidos");
    if(size<6)return narrate_mark_impossible(out,"programa de calculo truncado");
    flags=*p++;port_a=*p++;port_b=*p++;removed=*p++;extras=*p++;
    if(flags&~3 || (removed!=255 && removed>=in->n_comps) || extras>4 || end-p<extras*3+1)
        return narrate_mark_impossible(out,"restricoes invalidas");
    opamp_count=extras;
    for(i=0;i<extras;i++){
        if(p[0]>=in->n_nodes || p[1]>=in->n_nodes || p[2]>=in->n_nodes)
            return narrate_mark_impossible(out,"nos de AOP invalidos");
        memcpy(opamp_nodes[i],p,3);p+=3;
    }
    if(flags&3 && !solve_network(in,in->omega,65535,(flags&2)!=0))
        return narrate_mark_impossible(out,"rede singular: confira restricoes");
    i=*p++;
    while(i--) {
        const char *label,*formula,*unit;
        uint16_t len;uint8_t mode;
        LiveValue r;char buf[40];
        if(var_count>=LIVE_MAXVARS || p>=end)return narrate_mark_impossible(out,"limite de etapas excedido");
        label=(const char *)p;
        while(p<end && *p)p++;
        if(p>=end || p-(const uint8_t *)label>34)return false;
        p++;
        formula=(const char *)p;
        while(p<end && *p)p++;
        if(p>=end || p-(const uint8_t *)formula>37)return false;
        p++;
        unit=(const char *)p;
        while(p<end && *p)p++;
        if(p>=end || p-(const uint8_t *)unit>8 || end-p<4)return false;
        p++;
        mode=*p++;len=u16(p);p+=2;
        if(end-p<len || !eval(p,p+len,in,&r))
            return narrate_mark_impossible(out,"dominio invalido nos dados atuais");
        p+=len;vars[var_count++]=r;
        if(mode>2)return narrate_mark_impossible(out,"formato de etapa invalido");
        if(mode==0)continue; /* internal derived variable */
        if(formula[0]) {
            if(out->count>=NARRATE_MAXLINES)return narrate_mark_impossible(out,"resolucao excede o limite");
            lb_reset(&lb);lb_str(&lb,formula);narrate_commit(out,NCOL_BLUE,&lb);
        }
        if(mode==2)fmt_polar(buf,r.re,r.im,unit);
        else if(r.im!=0)fmt_rect(buf,r.re,r.im,unit);
        else if(!unit[0] || !strcmp(unit,"deg")) {
            fmt_num(buf,r.re);
            if(unit[0])strcat(buf," deg");
        }else fmt_eng(buf,r.re,unit);
        if(strlen(label)+3+strlen(buf)>37) {
            if(out->count+2>NARRATE_MAXLINES)return narrate_mark_impossible(out,"resolucao excede o limite");
            lb_reset(&lb);lb_str(&lb,label);lb_str(&lb," =");narrate_commit(out,NCOL_RED,&lb);
            lb_reset(&lb);lb_str(&lb,buf);narrate_commit(out,NCOL_RED,&lb);
            continue;
        }
        if(out->count>=NARRATE_MAXLINES)return narrate_mark_impossible(out,"resolucao excede o limite");
        lb_reset(&lb);lb_str(&lb,label);lb_str(&lb," = ");lb_str(&lb,buf);
        narrate_commit(out,NCOL_RED,&lb);
    }
    return p==end;
}
