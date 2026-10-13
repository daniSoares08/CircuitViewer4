/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */

#include "fmt.h"
#include <math.h>
#include <stdbool.h>

static uint8_t app_ch(char *dst, uint8_t pos, char c) {
    dst[pos++] = c;
    dst[pos] = '\0';
    return pos;
}

static uint8_t app_u32(char *dst, uint8_t pos, uint32_t v) {
    char tmp[10];
    uint8_t n = 0;
    if (v == 0) return app_ch(dst, pos, '0');
    while (v && n < sizeof(tmp)) {
        tmp[n++] = (char)('0' + v % 10);
        v /= 10;
    }
    while (n) pos = app_ch(dst, pos, tmp[--n]);
    return pos;
}

static uint8_t app_str(char *dst, uint8_t pos, const char *s) {
    while (*s) pos = app_ch(dst, pos, *s++);
    return pos;
}

/* Fixed-point print with a caller-chosen decimal count, trailing zeros
 * (and a bare trailing '.') trimmed. `whole`/`frac` already rounded. */
static uint8_t app_fixed(char *dst, uint8_t pos, bool neg, uint32_t whole,
                          uint32_t frac, uint8_t decimals) {
    char fdig[4];
    uint8_t i, keep;

    if (neg) pos = app_ch(dst, pos, '-');
    pos = app_u32(dst, pos, whole);
    if (decimals == 0 || frac == 0) return pos;

    for (i = 0; i < decimals; i++) {
        fdig[decimals - 1 - i] = (char)('0' + frac % 10);
        frac /= 10;
    }
    keep = decimals;
    while (keep > 0 && fdig[keep - 1] == '0') keep--;
    if (keep == 0) return pos;
    pos = app_ch(dst, pos, '.');
    for (i = 0; i < keep; i++) pos = app_ch(dst, pos, fdig[i]);
    return pos;
}

/* value >= 0, decimals in [0,3]; returns whole/frac split with frac scaled
 * to `decimals` digits and correctly carried on rounding (e.g. 99.996 with
 * 2 decimals -> whole=100, frac=0, not whole=99,frac=100). */
static void split_round(double value, uint8_t decimals, uint32_t *whole, uint32_t *frac) {
    static const uint32_t pow10[4] = { 1, 10, 100, 1000 };
    uint32_t scale = pow10[decimals];
    double scaled = value * (double)scale + 0.5;
    uint32_t total = (uint32_t)scaled;
    *whole = total / scale;
    *frac = total % scale;
}

uint8_t fmt_num(char *dst, double value) {
    bool neg = value < 0.0;
    double mag = neg ? -value : value;
    uint8_t decimals;
    uint32_t whole, frac;

    if (!(mag == mag) || mag > 1.0e12) { /* NaN or absurd */
        dst[0] = 'e'; dst[1] = 'r'; dst[2] = 'r'; dst[3] = '\0';
        return 3;
    }
    if (mag < 10.0) decimals = 3;
    else if (mag < 100.0) decimals = 2;
    else if (mag < 1000.0) decimals = 1;
    else decimals = 0;
    split_round(mag, decimals, &whole, &frac);
    if (whole >= 1000 && decimals > 0) { /* rounding pushed us up a decade */
        decimals--;
        split_round(mag, decimals, &whole, &frac);
    }
    return app_fixed(dst, 0, neg, whole, frac, decimals);
}

/* Shared engineering-notation split: fills the rounded mantissa (neg/whole/
 * frac/decimals) and picks the k/m/u prefix. */
static void eng_scale(double mag, double *div, const char **prefix);
static void eng_split(double value, bool *neg, uint32_t *whole, uint32_t *frac,
                      uint8_t *decimals, const char **prefix) {
    double mag;
    double mant;

    *neg = value < 0.0;
    mag = *neg ? -value : value;
    { double div;eng_scale(mag,&div,prefix);mant=mag/div; }
    if (mant < 10.0) *decimals = 3;
    else if (mant < 100.0) *decimals = 2;
    else *decimals = 1;
    split_round(mant, *decimals, whole, frac);
    if (*whole >= 1000) { /* rounded into the next prefix (rare, e.g. 999.96) */
        *whole = 1; *frac = 0; *decimals = 0;
        if ((*prefix)[0] == 0) *prefix = "k";
        else if ((*prefix)[0] == 'm') *prefix = "";
        else if ((*prefix)[0] == 'u') *prefix = "m";
        else if ((*prefix)[0] == 'n') *prefix = "u";
        else if ((*prefix)[0] == 'p') *prefix = "n";
        else if ((*prefix)[0] == 'k') *prefix = "M";
        else if ((*prefix)[0] == 'M') *prefix = "G";
    }
}

uint8_t fmt_eng(char *dst, double value, const char *unit) {
    bool neg;
    uint32_t whole, frac;
    uint8_t decimals, pos;
    const char *prefix;

    eng_split(value, &neg, &whole, &frac, &decimals, &prefix);
    pos = app_fixed(dst, 0, neg, whole, frac, decimals);
    if (unit && unit[0]) {
        pos = app_ch(dst, pos, ' ');
        pos = app_str(dst, pos, prefix);
        pos = app_str(dst, pos, unit);
    } else if (prefix[0]) {
        pos = app_ch(dst, pos, ' ');
        pos = app_str(dst, pos, prefix);
    }
    return pos;
}

uint8_t fmt_label(char *dst, double value, const char *suffix) {
    bool neg;
    uint32_t whole, frac;
    uint8_t decimals, pos;
    const char *prefix;

    /* compact form for on-circuit labels: no space anywhere, prefix and
     * suffix concatenated directly onto the number ("6k", "12V", "4mA"). */
    eng_split(value, &neg, &whole, &frac, &decimals, &prefix);
    pos = app_fixed(dst, 0, neg, whole, frac, decimals);
    pos = app_str(dst, pos, prefix);
    if (suffix && suffix[0]) pos = app_str(dst, pos, suffix);
    return pos;
}

/* ---- phasor formatting -------------------------------------------------- */
uint8_t fmt_rect_label(char *dst, double re, double im) {
    uint8_t n=0;
    double mag=cx_mag(re,im);
    if (fabs(re)<mag*1e-6) re=0;
    if (fabs(im)<mag*1e-6) im=0;
    if (re!=0 || im==0) n=fmt_label(dst,re,"");
    if (im!=0) {
        if (re!=0) n=app_ch(dst,n,im<0?'-':'+');
        else if (im<0) n=app_ch(dst,n,'-');
        n=app_ch(dst,n,'j');
        n+=fmt_label(dst+n,fabs(im),"");
    }
    return n;
}
uint8_t fmt_polar_label(char *dst, double re, double im, const char *suffix) {
    uint8_t n=fmt_label(dst,cx_mag(re,im),suffix);
    double angle=cx_deg(re,im);
    uint32_t whole,frac;
    n=app_str(dst,n,"/_");
    split_round(fabs(angle),1,&whole,&frac);
    return app_fixed(dst,n,angle<0,whole,frac,1);
}

/* Below this, a component of a phasor is treated as exactly zero so a result
 * prints "10 V" instead of "10 + j0.0000001 V". Relative to the magnitude,
 * because an answer in microamps and one in kilovolts need different floors. */
static bool negligible(double part, double mag) {
    double floor_ = mag * 1e-6;
    if (floor_ < 1e-12) floor_ = 1e-12;
    return fabs(part) < floor_;
}

double cx_mag(double re, double im) {
    return sqrt(re * re + im * im);
}

double cx_deg(double re, double im) {
    /* atan2 already returns (-pi, pi], so the degree result lands in
     * (-180, 180] with no extra normalisation. */
    return atan2(im, re) * (180.0 / 3.14159265358979323846);
}

/* Engineering scale factor and prefix chosen from `mag`. Both parts of a
 * phasor must share ONE scale, otherwise the prefix on the real part is
 * left orphaned from its unit and you get nonsense like "50 m - j50 mS"
 * instead of "50 - j50 mS". */
static void eng_scale(double mag, double *div, const char **prefix) {
    *prefix = "";
    *div = 1.0;
    if (mag == 0.0) return;
    if (mag >= 999.95e6) { *prefix = "G"; *div = 1e9; }
    else if (mag >= 999.95e3) { *prefix = "M"; *div = 1e6; }
    else if (mag >= 999.95) { *prefix = "k"; *div = 1000.0; }
    else if (mag < 0.9995) {
        if (mag >= 0.0009995) { *prefix = "m"; *div = 1.0e-3; }
        else if (mag >= 0.0000009995) { *prefix = "u"; *div = 1.0e-6; }
        else if (mag >= 0.0000000009995) { *prefix = "n"; *div = 1.0e-9; }
        else { *prefix = "p"; *div = 1.0e-12; }
    }
}

/* Fixed-point print of `v` already scaled into its prefix, with the decimal
 * count fmt_eng would have used for that magnitude. */
static uint8_t app_scaled(char *dst, uint8_t pos, double v) {
    bool neg = v < 0.0;
    double m = neg ? -v : v;
    uint32_t whole, frac;
    uint8_t decimals;

    if (m < 10.0) decimals = 3;
    else if (m < 100.0) decimals = 2;
    else decimals = 1;
    split_round(m, decimals, &whole, &frac);
    return app_fixed(dst, pos, neg, whole, frac, decimals);
}

uint8_t fmt_rect(char *dst, double re, double im, const char *unit) {
    double mag = cx_mag(re, im);
    bool re_zero = negligible(re, mag);
    bool im_zero = negligible(im, mag);
    double div;
    const char *prefix;
    uint8_t pos = 0;

    if (re_zero && im_zero) return fmt_eng(dst, 0.0, unit);
    if (im_zero) return fmt_eng(dst, re, unit);

    eng_scale(mag, &div, &prefix);

    if (!re_zero) {
        pos = app_scaled(dst, pos, re / div);
        pos = app_str(dst, pos, im < 0.0 ? " - j" : " + j");
    } else {
        if (im < 0.0) pos = app_ch(dst, pos, '-');
        pos = app_ch(dst, pos, 'j');
    }
    pos = app_scaled(dst, pos, fabs(im) / div);
    if (unit && unit[0]) {
        pos = app_ch(dst, pos, ' ');
        pos = app_str(dst, pos, prefix);
        pos = app_str(dst, pos, unit);
    } else if (prefix[0]) {
        pos = app_ch(dst, pos, ' ');
        pos = app_str(dst, pos, prefix);
    }
    return pos;
}

uint8_t fmt_polar(char *dst, double re, double im, const char *unit) {
    double mag = cx_mag(re, im);
    double deg = cx_deg(re, im);
    uint8_t pos = (!unit || !unit[0]) && mag>=0.0009995 && mag<1e6 ? fmt_num(dst,mag) : fmt_eng(dst, mag, unit);

    /* "/_" is the project's ASCII stand-in for the angle sign; the
     * calculator font has no U+2220 and the whole codebase is ASCII-only. */
    pos = app_str(dst, pos, " /_");
    if (negligible(im, mag) && re >= 0.0) deg = 0.0;   /* avoid "-0deg" */
    pos += fmt_num(dst + pos, deg);
    pos = app_str(dst,pos," deg");
    return pos;
}
