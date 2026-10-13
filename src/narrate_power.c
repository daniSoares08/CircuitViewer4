#include "narrate_power.h"
#include "narrate.h"
#include "fmt.h"
#include <math.h>

static void lb_rect_power(LineBuf *lb, double re, double im, const char *unit) {
    char text[40];
    fmt_rect(text, re, im, unit); lb_str(lb, text);
}

static void lb_polar_power(LineBuf *lb, double re, double im, const char *unit) {
    char text[40];
    fmt_polar(text, re, im, unit);
    lb_str(lb, text);
}

static void from_polar(double mag, double deg, double *re, double *im) {
    double rad = deg * 3.14159265358979323846 / 180.0;
    *re = mag * cos(rad); *im = mag * sin(rad);
}

bool narrate_max_power(const float *p, uint8_t n, Narration *out) {
    double v2, vmag, vrms, rth, pmax;
    LineBuf lb;
    narrate_reset(out);
    if (n < 5 || p[2] <= 0.0f) return narrate_mark_impossible(out, "parametros de Thevenin invalidos");
    v2 = (double)p[0] * p[0] + (double)p[1] * p[1];
    vmag = sqrt(v2); rth = p[2];
    vrms = p[4] != 0.0f ? vmag / sqrt(2.0) : vmag;
    pmax = v2 / ((p[4] != 0.0f ? 8.0 : 4.0) * rth);
    lb_reset(&lb); lb_str(&lb, "# 1) Casamento conjugado"); narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, "Zth = "); lb_rect_power(&lb, p[2], p[3], "ohm");
    narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "ZL = conj(Zth) = ");
    lb_rect_power(&lb, p[2], -p[3], "ohm"); narrate_commit(out, NCOL_RED, &lb);
    lb_reset(&lb); lb_str(&lb, "Logo RL = Rth = "); lb_eng(&lb, rth, "ohm");
    narrate_commit(out, NCOL_BLACK, &lb);

    lb_reset(&lb); lb_str(&lb, "# 2) Converta a tensao para RMS"); narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, p[4] != 0.0f ? "Vrms = Vpico / sqrt(2)" : "A tensao fornecida ja e RMS");
    narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "Vrms = "); lb_eng(&lb, vrms, "V");
    narrate_commit(out, NCOL_RED, &lb);

    lb_reset(&lb); lb_str(&lb, "# 3) Potencia media maxima"); narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, "Pmax = Vrms^2 / (4 Rth)"); narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "Pmax = "); lb_num(&lb, vrms); lb_str(&lb, "^2 / (4 x ");
    lb_num(&lb, rth); lb_str(&lb, ")"); narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "Pmax = "); lb_eng(&lb, pmax, "W"); narrate_commit(out, NCOL_RED, &lb);
    return true;
}

bool narrate_three_phase(const float *p, uint8_t n, Narration *out) {
    double s, vph, pf, iph, iline, vline, phi;
    LineBuf lb;
    narrate_reset(out);
    if (n < 5 || p[0] <= 0.0f || p[1] <= 0.0f || p[2] <= 0.0f || p[2] > 1.0f)
        return narrate_mark_impossible(out, "parametros trifasicos invalidos");
    s = p[0]; vph = p[1]; pf = p[2]; iph = s / (3.0 * vph);
    if (p[3] == 0.0f) { iline = iph; vline = sqrt(3.0) * vph; }
    else { iline = sqrt(3.0) * iph; vline = vph; }
    phi = acos(pf) * 180.0 / 3.14159265358979323846;
    if (p[4] != 0.0f) phi = -phi;
    lb_reset(&lb); lb_str(&lb, "# 1) Dados trifasicos");
    narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, "|S3f| = "); lb_eng(&lb, s, "VA"); narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "Vfase = "); lb_eng(&lb, vph, "V"); lb_str(&lb, "; fp = "); lb_num(&lb, pf);
    narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "phi = acos(fp) = "); lb_num(&lb, fabs(phi)); lb_str(&lb, " deg");
    narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, p[4] != 0.0f ? "Atrasado: angulo de I = -phi" : "Adiantado: angulo de I = +phi");
    narrate_commit(out, NCOL_BLACK, &lb);

    lb_reset(&lb); lb_str(&lb, "# 2) Corrente de fase"); narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, "|S3f| = 3 Vfase Ifase"); narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "Ifase = |S3f| / (3 Vfase)"); narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "Ifase = "); lb_eng(&lb, iph, "A"); narrate_commit(out, NCOL_RED, &lb);

    lb_reset(&lb); lb_str(&lb, "# 3) Relacoes de linha"); narrate_commit(out, NCOL_BLUE, &lb);
    lb_reset(&lb); lb_str(&lb, p[3] == 0.0f ? "Em Y: Ilinha=Ifase" : "Em delta: Ilinha=sqrt(3)Ifase");
    narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, p[3] == 0.0f ? "Em Y: Vlinha=sqrt(3)Vfase" : "Em delta: Vlinha=Vfase");
    narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "Ilinha = "); lb_eng(&lb, iline, "A"); narrate_commit(out, NCOL_RED, &lb);
    lb_reset(&lb); lb_str(&lb, "Angulo(Ilinha) = "); lb_num(&lb, phi); lb_str(&lb, " deg");
    narrate_commit(out, NCOL_BLACK, &lb);
    lb_reset(&lb); lb_str(&lb, "Vlinha = "); lb_eng(&lb, vline, "V"); narrate_commit(out, NCOL_RED, &lb);
    lb_reset(&lb); lb_str(&lb, "Ilinha="); lb_eng(&lb, iline, "A"); lb_str(&lb, "; Vlinha="); lb_eng(&lb, vline, "V");
    narrate_commit(out, NCOL_RED, &lb);
    return true;
}

bool narrate_power_profile(uint8_t profile, const float *p, uint8_t n,
                           Narration *out) {
    LineBuf lb;
    narrate_reset(out);
    if (profile == POWER_PROFILE_TRIANGLE) {
        double q, phi, s, pw;
        if (n < 2) return narrate_mark_impossible(out, "parametros insuficientes");
        q = p[0]; phi = p[1] * 3.14159265358979323846 / 180.0;
        s = q / sin(phi); pw = s * cos(phi);
        lb_reset(&lb); lb_str(&lb, "# Triangulo de potencia"); narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "Q = |S| sen(phi)"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "|S| = Q / sen(phi)"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "|S| = "); lb_eng(&lb, s, "VA"); narrate_commit(out, NCOL_RED, &lb);
        lb_reset(&lb); lb_str(&lb, "P = "); lb_eng(&lb, pw, "W"); narrate_commit(out, NCOL_BLACK, &lb);
        return true;
    }
    if (profile == POWER_PROFILE_LOAD_SUM) {
        double sa, qa, sb, qb, pc, qc, vr, vi, sr, si, den, ir, ii, smag, pf;
        if (n < 10) return narrate_mark_impossible(out, "parametros insuficientes");
        sa = p[0] * p[1]; qa = (p[2] < 0 ? -1.0 : 1.0) * p[0] * sqrt(1.0 - p[1] * p[1]);
        sb = p[3] * p[4]; qb = (p[5] < 0 ? -1.0 : 1.0) * p[3] * sqrt(1.0 - p[4] * p[4]);
        pc = p[6]; qc = p[7]; sr = sa + sb + pc; si = qa + qb + qc;
        from_polar(p[8], p[9], &vr, &vi); den = vr * vr + vi * vi;
        ir = (sr * vr + si * vi) / den;
        ii = (si * vr - sr * vi) / den;
        ii = -ii; /* I = conjugado(S/V) */
        smag = sqrt(sr * sr + si * si); pf = fabs(sr) / smag;
        lb_reset(&lb); lb_str(&lb, "# 1) Potencias complexas"); narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "SA = "); lb_rect_power(&lb, sa, qa, "VA"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "SB = "); lb_rect_power(&lb, sb, qb, "VA"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "SC = "); lb_rect_power(&lb, pc, qc, "VA"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "St = SA + SB + SC"); narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "St = "); lb_rect_power(&lb, sr, si, "VA"); narrate_commit(out, NCOL_RED, &lb);
        lb_reset(&lb); lb_str(&lb, "# 2) I = conjugado(St/V)"); narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "I = "); lb_polar_power(&lb, ir, ii, "A"); narrate_commit(out, NCOL_RED, &lb);
        lb_reset(&lb); lb_str(&lb, "FP = "); lb_num(&lb, pf); lb_str(&lb, si < 0 ? " adiantado" : " atrasado"); narrate_commit(out, NCOL_RED, &lb);
        return true;
    }
    if (profile == POWER_PROFILE_PF_CORRECTION) {
        double v, f, r, x, den, pw, q, pf, cap;
        if (n < 4) return narrate_mark_impossible(out, "parametros insuficientes");
        v = p[0]; f = p[1]; r = p[2]; x = p[3]; den = r * r + x * x;
        if (den <= 1e-18 || f <= 0.0) return narrate_mark_impossible(out, "dados invalidos");
        pw = v * v * r / den; q = v * v * x / den; pf = r / sqrt(den);
        cap = q / (2.0 * 3.14159265358979323846 * f * v * v);
        lb_reset(&lb); lb_str(&lb, "# 1) Potencia da carga"); narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "P = V^2 R / |Z|^2"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "P = "); lb_eng(&lb, pw, "W"); narrate_commit(out, NCOL_RED, &lb);
        lb_reset(&lb); lb_str(&lb, "Q = "); lb_eng(&lb, q, "VAR"); narrate_commit(out, NCOL_RED, &lb);
        lb_reset(&lb); lb_str(&lb, "FP = "); lb_num(&lb, pf); lb_str(&lb, " atrasado"); narrate_commit(out, NCOL_RED, &lb);
        lb_reset(&lb); lb_str(&lb, "# 2) Correcao para FP=1"); narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "Qc = -w C V^2 = -Q"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "C = Q/(2 pi f V^2)"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "C = "); lb_eng(&lb, cap, "F"); narrate_commit(out, NCOL_RED, &lb);
        return true;
    }
    if (profile == POWER_PROFILE_INSTANTANEOUS) {
        double vm, va, im, ia, w, amp, avg;
        if (n < 5) return narrate_mark_impossible(out, "parametros insuficientes");
        vm = p[0]; va = p[1]; im = p[2]; ia = p[3]; w = p[4];
        amp = 0.5 * vm * im;
        avg = amp * cos((va - ia) * 3.14159265358979323846 / 180.0);
        lb_reset(&lb); lb_str(&lb, "# 1) Forma padrao dos sinais"); narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "v=Vm cos(wt+thetaV)"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "i=Im cos(wt+thetaI)"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "# 2) Produto seno-cosseno"); narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "p(t)=Pmed+A cos(2wt+thetaV+thetaI)"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "Pmed = Vm Im cos(thetaV-thetaI)/2"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "Pmed = "); lb_eng(&lb, avg, "W"); narrate_commit(out, NCOL_RED, &lb);
        lb_reset(&lb); lb_str(&lb, "A = "); lb_eng(&lb, amp, "W"); lb_str(&lb, "; 2w = "); lb_num(&lb, 2.0 * w); narrate_commit(out, NCOL_RED, &lb);
        lb_reset(&lb); lb_str(&lb, "fase oscilante = "); lb_num(&lb, va + ia); lb_str(&lb, " deg"); narrate_commit(out, NCOL_RED, &lb);
        return true;
    }
    return narrate_mark_impossible(out, "perfil de potencia desconhecido");
}

bool narrate_three_phase_profile(uint8_t profile, const float *p, uint8_t n,
                                 Narration *out) {
    LineBuf lb;
    narrate_reset(out);
    if (profile == THREE_PROFILE_DELTA_RELATION) {
        if (n < 1) return narrate_mark_impossible(out, "parametros insuficientes");
        lb_reset(&lb); lb_str(&lb, "# Carga ligada em triangulo"); narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "Vlinha = Vfase"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "Vlinha = "); lb_eng(&lb, p[0], "V"); narrate_commit(out, NCOL_RED, &lb);
        return true;
    }
    if (profile == THREE_PROFILE_STAR_DELTA || profile == THREE_PROFILE_DELTA_STAR ||
        profile == THREE_PROFILE_STAR_STAR) {
        double vmag, vang, zlr, zli, zdr, zdi, zyr, zyi, dr, di, den;
        double ir, ii, br, bi, cr, ci;
        if (n < 6) return narrate_mark_impossible(out, "parametros insuficientes");
        vmag = p[0]; vang = p[1]; zlr = p[2]; zli = p[3]; zdr = p[4]; zdi = p[5];
        if (profile == THREE_PROFILE_STAR_DELTA) {
            zyr = zdr / 3.0; zyi = zdi / 3.0;
        } else if (profile == THREE_PROFILE_DELTA_STAR) {
            vmag /= sqrt(3.0); vang -= 30.0;
            zyr = zdr; zyi = zdi;
        } else {
            zyr = zdr; zyi = zdi;
        }
        dr = zlr + zyr; di = zli + zyi; den = dr * dr + di * di;
        from_polar(vmag, vang, &br, &bi);
        ir = (br * dr + bi * di) / den; ii = (bi * dr - br * di) / den;
        from_polar(cx_mag(ir, ii), cx_deg(ir, ii) - 120.0, &br, &bi);
        from_polar(cx_mag(ir, ii), cx_deg(ir, ii) + 120.0, &cr, &ci);
        lb_reset(&lb);
        lb_str(&lb, profile == THREE_PROFILE_STAR_DELTA ?
               "# 1) Delta equivalente em Y" : "# 1) Impedancia por fase");
        narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb);
        lb_str(&lb, profile == THREE_PROFILE_STAR_DELTA ? "ZY = Zdelta/3 = " : "ZY = ");
        lb_rect_power(&lb, zyr, zyi, "ohm"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "# 2) Corrente da fase a"); narrate_commit(out, NCOL_BLUE, &lb);
        lb_reset(&lb); lb_str(&lb, "Ia = Va/(Zlinha+ZY)"); narrate_commit(out, NCOL_BLACK, &lb);
        lb_reset(&lb); lb_str(&lb, "Ia = "); lb_polar_power(&lb, ir, ii, "A"); narrate_commit(out, NCOL_RED, &lb);
        lb_reset(&lb); lb_str(&lb, "Ib = "); lb_polar_power(&lb, br, bi, "A"); narrate_commit(out, NCOL_RED, &lb);
        lb_reset(&lb); lb_str(&lb, "Ic = "); lb_polar_power(&lb, cr, ci, "A"); narrate_commit(out, NCOL_RED, &lb);
        return true;
    }
    return narrate_mark_impossible(out, "perfil trifasico desconhecido");
}
