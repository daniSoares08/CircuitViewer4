/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */

#include "cv3.h"
#include "engine.h"
#include "narrate.h"
#include "fmt.h"
#include <string.h>
#include <math.h>

static void appvar_missing_loop(void);

/* ---- main menu: single flat list, book-ordered (see tools/cv4_content.py) */

static void draw_main_menu(uint8_t selected) {
    uint8_t i;
    uint8_t first = 0;
    uint8_t visible = 10;

    gfx_FillScreen(COL_WHITE);
    gfx_SetTextFGColor(COL_BLACK);
    print_center("CIRCVIE4", 8);
    gfx_SetColor(COL_BLACK);
    gfx_HorizLine(0, 24, SCREEN_W);
    gfx_SetTextFGColor(COL_GRAY);
    prn("Conteudo:", 10, 30);

    if (selected >= visible) first = (uint8_t)(selected - visible + 1);

    for (i = 0; i < visible && first + i < menu_count; i++) {
        uint8_t item = (uint8_t)(first + i);
        int y = 46 + i * 17;
        if (item == selected) {
            gfx_SetColor(COL_LIGHT);
            gfx_FillRectangle(12, y - 3, 296, 15);
            gfx_SetColor(COL_BLUE);
            gfx_Rectangle(12, y - 3, 296, 15);
            gfx_SetTextFGColor(COL_BLUE);
        } else {
            gfx_SetTextFGColor(COL_BLACK);
        }
        prn(menu_items[item].title, 22, y);
    }

    if (first > 0) prn("^", 300, 32);
    if (first + visible < menu_count) prn("v", 300, 212);

    draw_footer_menu();
}

static int main_menu_loop(void) {
    uint8_t selected = 0;
    bool redraw = true;

    wait_key_release();
    if (menu_count == 0) {
        gfx_FillScreen(COL_WHITE);
        gfx_SetTextFGColor(COL_BLACK);
        print_center("CIRCVIE4", 8);
        gfx_SetColor(COL_BLACK);
        gfx_HorizLine(0, 24, SCREEN_W);
        print_center("Sem conteudo carregado.", 82);
        draw_footer_menu();
        gfx_SwapDraw();
        while (1) { check_on_exit(); kb_Scan(); delay(15); }
    }

    while (1) {
        check_on_exit();
        kb_Scan();

        if (redraw) {
            draw_main_menu(selected);
            gfx_SwapDraw();
            redraw = false;
        }

        if (pressed_once(kb_KeyDown) && selected + 1 < menu_count) {
            selected++;
            redraw = true;
        }
        if (pressed_once(kb_KeyUp) && selected > 0) {
            selected--;
            redraw = true;
        }
        if (pressed_once(kb_KeyEnter)) {
            wait_key_release();
            return selected;
        }
        delay(15);
    }
}

/* ---- numeric entry (DOC.md section 6 pattern) ------------------------- */

static void input_line(char *buf, uint8_t maxlen, const char *prompt,
                       const char *hint) {
    uint8_t idx = 0;
    bool redraw = true;
    buf[0] = '\0';

    wait_key_release();
    for (;;) {
        check_on_exit();
        kb_Scan();

        if (redraw) {
            gfx_FillScreen(COL_WHITE);
            gfx_SetTextFGColor(COL_BLACK);
            prn(prompt, 8, 40);
            gfx_SetTextFGColor(COL_GRAY);
            prn("Valor atual:", 8, 60);
            prn(hint, 8, 76);
            gfx_SetTextFGColor(COL_BLACK);
            prn("Novo valor:", 8, 104);
            prn(buf, 8, 122);
            gfx_SetColor(COL_BLACK);
            gfx_VertLine((int)(8 + gfx_GetStringWidth(buf)), 120, 12);
            draw_footer_edit();
            prn("ENTER=ok  DEL=apaga  CLEAR=cancela", 2, 229);
            gfx_SwapDraw();
            redraw = false;
        }

        if (pressed_once(kb_KeyEnter)) { wait_key_release(); return; }
        if (pressed_once(kb_KeyClear)) { buf[0] = '\0'; wait_key_release(); return; }
        if (pressed_once(kb_KeyDel) && idx > 0) { idx--; buf[idx] = '\0'; redraw = true; }

        if (idx < maxlen - 1) {
            char c = 0;
            if (pressed_once(kb_Key0)) c = '0';
            else if (pressed_once(kb_Key1)) c = '1';
            else if (pressed_once(kb_Key2)) c = '2';
            else if (pressed_once(kb_Key3)) c = '3';
            else if (pressed_once(kb_Key4)) c = '4';
            else if (pressed_once(kb_Key5)) c = '5';
            else if (pressed_once(kb_Key6)) c = '6';
            else if (pressed_once(kb_Key7)) c = '7';
            else if (pressed_once(kb_Key8)) c = '8';
            else if (pressed_once(kb_Key9)) c = '9';
            else if (pressed_once(kb_KeyDecPnt)) c = '.';
            else if (pressed_once(kb_KeyChs) || pressed_once(kb_KeySub)) c = '-';
            if (c) { buf[idx++] = c; buf[idx] = '\0'; redraw = true; }
        }
        delay(15);
    }
}

static float parse_float(const char *s) {
    bool neg = false;
    float v = 0.0f;
    float frac = 0.0f;
    float place = 0.1f;
    bool after_dot = false;

    if (*s == '-') { neg = true; s++; }
    while (*s) {
        if (*s == '.') { after_dot = true; s++; continue; }
        if (*s < '0' || *s > '9') { s++; continue; }
        if (after_dot) { frac += (float)(*s - '0') * place; place *= 0.1f; }
        else { v = v * 10.0f + (float)(*s - '0'); }
        s++;
    }
    v += frac;
    return neg ? -v : v;
}

/* ---- live edit UI ------------------------------------------------------- */

static const char *kind_short_name(uint8_t kind) {
    switch (kind) {
    case CK_RES: return "Resistores";
    case CK_VSRC: return "Fontes de tensao";
    case CK_ISRC: return "Fontes de corrente";
    case CK_CAP: return "Capacitores";
    case CK_IND: return "Indutores";
    case CK_DVS: return "Fontes V dependentes";
    case CK_DIS: return "Fontes I dependentes";
    case CK_Z: return "Impedancias complexas";
    default: return "?";
    }
}

static bool kind_has_direction(uint8_t kind) {
    return kind == CK_VSRC || kind == CK_ISRC || kind == CK_DVS ||
           kind == CK_DIS || kind == CK_ARROW;
}

static void draw_simple_list(const char *title, const char *const *items,
                             uint8_t count, uint8_t selected) {
    uint8_t i;
    uint8_t first = 0;
    uint8_t visible = 9;

    gfx_FillScreen(COL_WHITE);
    gfx_SetTextFGColor(COL_BLACK);
    print_center(title, 8);
    gfx_SetColor(COL_BLACK);
    gfx_HorizLine(0, 24, SCREEN_W);

    if (selected >= visible) first = (uint8_t)(selected - visible + 1);
    for (i = 0; i < visible && first + i < count; i++) {
        uint8_t item = (uint8_t)(first + i);
        int y = 40 + i * 19;
        if (item == selected) {
            gfx_SetColor(COL_LIGHT);
            gfx_FillRectangle(12, y - 3, 296, 17);
            gfx_SetColor(COL_BLUE);
            gfx_Rectangle(12, y - 3, 296, 17);
            gfx_SetTextFGColor(COL_BLUE);
        } else {
            gfx_SetTextFGColor(COL_BLACK);
        }
        prn(items[item], 22, y);
    }
    draw_footer_edit();
}

#define EDIT_MAXITEMS 64 /* scalar expressions can have >16 original givens */
static char edit_item_buf[EDIT_MAXITEMS][40]; /* value + polarity suffix <=36 */
static const char *edit_item_ptrs[EDIT_MAXITEMS];

static void fill_comp_label(char *dst, uint8_t within_kind_num, const EditComp *c) {
    uint8_t pos;
    const char *unit = unit_for_kind(c->kind);
    char val[28];
    double v = (c->flags & 1) ? -(double)c->value : (double)c->value;

    switch (c->kind) {
    case CK_RES: dst[0] = 'R'; break;
    case CK_VSRC: dst[0] = 'V'; break;
    case CK_ISRC: dst[0] = 'I'; break;
    case CK_CAP: dst[0] = 'C'; break;
    case CK_IND: dst[0] = 'L'; break;
    case CK_DVS: dst[0] = 'V'; break;
    case CK_DIS: dst[0] = 'I'; break;
    case CK_Z: dst[0] = 'Z'; break;
    default: dst[0] = 'X'; break;
    }
    dst[1] = '\0';
    {
        uint8_t n = within_kind_num;
        char tmp[4]; uint8_t tn = 0;
        if (n == 0) tmp[tn++] = '0';
        while (n) { tmp[tn++] = (char)('0' + n % 10); n /= 10; }
        pos = 1;
        while (tn) dst[pos++] = tmp[--tn];
    }
    dst[pos++] = ':'; dst[pos++] = ' ';
    if (c->kind == CK_Z || (((c->kind == CK_VSRC || c->kind == CK_ISRC ||
                              c->kind == CK_DVS || c->kind == CK_DIS)) &&
                            c->value_im != 0.0f))
        fmt_polar(val, v, (c->flags & 1) ? -(double)c->value_im : (double)c->value_im, unit);
    else
        fmt_eng(val, v, unit);
    { uint8_t i; for (i = 0; val[i] && pos < 24; i++) dst[pos++] = val[i]; }
    dst[pos] = '\0';
}

static void edit_values_component_loop(uint8_t kind) {
    uint8_t idx[EDIT_MAXITEMS];
    uint8_t n = 0;
    uint8_t total = exercise_comp_count();
    uint8_t i, within;
    uint8_t selected = 0;
    bool redraw = true;

    within = 1;
    for (i = 0; i < total && n < EDIT_MAXITEMS; i++) {
        EditComp *c = exercise_comp(i);
        if (c && c->kind == kind) {
            idx[n] = i;
            fill_comp_label(edit_item_buf[n], within, c);
            edit_item_ptrs[n] = edit_item_buf[n];
            n++;
            within++;
        }
    }
    if (n == 0) return;

    wait_key_release();
    while (1) {
        check_on_exit();
        kb_Scan();
        if (redraw) {
            draw_simple_list(kind_short_name(kind), edit_item_ptrs, n, selected);
            gfx_SwapDraw();
            redraw = false;
        }
        if (pressed_once(kb_KeyClear)) { wait_key_release(); return; }
        if (pressed_once(kb_KeyDown) && selected + 1 < n) { selected++; redraw = true; }
        if (pressed_once(kb_KeyUp) && selected > 0) { selected--; redraw = true; }
        if (pressed_once(kb_KeyEnter)) {
            EditComp *c = exercise_comp(idx[selected]);
            char buf[16];
            char hint[20];
            bool complex_value = c->kind == CK_Z || c->kind == CK_VSRC ||
                                 c->kind == CK_ISRC || c->kind == CK_DVS ||
                                 c->kind == CK_DIS;
            double curv = complex_value ? cx_mag(c->value, c->value_im) :
                          ((c->flags & 1) ? -(double)c->value : (double)c->value);
            fmt_eng(hint, curv, unit_for_kind(c->kind));
            input_line(buf, sizeof(buf), "Novo valor (numero):", hint);
            if (buf[0]) {
                float nv = parse_float(buf);
                edit_comp_set_magnitude(c,nv);
                exercise_apply_edit();
                fill_comp_label(edit_item_buf[selected], selected + 1, c);
            }
            wait_key_release();
            redraw = true;
        }
        delay(15);
    }
}

static void edit_values_menu_loop(void) {
    uint8_t seen_kinds[9];
    uint8_t n_kinds = 0;
    uint8_t total = exercise_comp_count();
    uint8_t i, k, selected = 0;
    bool redraw = true;

    for (k = 0; k <= CK_Z; k++) {
        if (k == CK_ARROW) continue;
        bool present = false;
        for (i = 0; i < total; i++) {
            EditComp *c = exercise_comp(i);
            if (c && c->kind == k) { present = true; break; }
        }
        if (present) seen_kinds[n_kinds++] = k;
    }
    if (n_kinds == 0) return;
    for (i = 0; i < n_kinds; i++) {
        strcpy(edit_item_buf[i], kind_short_name(seen_kinds[i]));
        edit_item_ptrs[i] = edit_item_buf[i];
    }

    wait_key_release();
    while (1) {
        check_on_exit();
        kb_Scan();
        if (redraw) {
            draw_simple_list("Editar valores", edit_item_ptrs, n_kinds, selected);
            gfx_SwapDraw();
            redraw = false;
        }
        if (pressed_once(kb_KeyClear)) { wait_key_release(); return; }
        if (pressed_once(kb_KeyDown) && selected + 1 < n_kinds) { selected++; redraw = true; }
        if (pressed_once(kb_KeyUp) && selected > 0) { selected--; redraw = true; }
        if (pressed_once(kb_KeyEnter)) {
            wait_key_release();
            edit_values_component_loop(seen_kinds[selected]);
            redraw = true;
        }
        delay(15);
    }
}

static void edit_directions_loop(void) {
    uint8_t idx[EDIT_MAXITEMS];
    uint8_t n = 0;
    uint8_t total = exercise_comp_count();
    uint8_t i, selected = 0;
    uint8_t within[9];
    bool redraw = true;

    for (i = 0; i < 9; i++) within[i] = 1;
    for (i = 0; i < total && n < EDIT_MAXITEMS; i++) {
        EditComp *c = exercise_comp(i);
        if (c && kind_has_direction(c->kind)) {
            idx[n] = i;
            if (c->kind == CK_ARROW) {
                strcpy(edit_item_buf[n], "Seta de corrente: ");
                strcat(edit_item_buf[n], c->flags & 1 ? "invertida" : "normal");
            } else {
                fill_comp_label(edit_item_buf[n], within[c->kind], c);
                strcat(edit_item_buf[n], c->flags & 1 ? " (invertida)" : "");
                within[c->kind]++;
            }
            edit_item_ptrs[n] = edit_item_buf[n];
            n++;
        }
    }
    if (n == 0) return;

    wait_key_release();
    while (1) {
        check_on_exit();
        kb_Scan();
        if (redraw) {
            draw_simple_list("Editar direcoes/polaridade", edit_item_ptrs, n, selected);
            gfx_SwapDraw();
            redraw = false;
        }
        if (pressed_once(kb_KeyClear)) { wait_key_release(); return; }
        if (pressed_once(kb_KeyDown) && selected + 1 < n) { selected++; redraw = true; }
        if (pressed_once(kb_KeyUp) && selected > 0) { selected--; redraw = true; }
        if (pressed_once(kb_KeyEnter)) {
            EditComp *c = exercise_comp(idx[selected]);
            c->flags = (uint8_t)(c->flags ^ 1);
            exercise_apply_edit();
            if (c->kind == CK_ARROW) {
                strcpy(edit_item_buf[selected], "Seta de corrente: ");
                strcat(edit_item_buf[selected], c->flags & 1 ? "invertida" : "normal");
            } else {
                fill_comp_label(edit_item_buf[selected], 1, c);
                strcat(edit_item_buf[selected], c->flags & 1 ? " (invertida)" : "");
            }
            wait_key_release();
            redraw = true;
        }
        delay(15);
    }
}

static bool kind_has_phase(uint8_t kind) {
    return kind == CK_VSRC || kind == CK_ISRC || kind == CK_DVS ||
           kind == CK_DIS || kind == CK_Z;
}

static void edit_phases_loop(void) {
    uint8_t idx[EDIT_MAXITEMS], n = 0, i, selected = 0;
    bool redraw = true;
    for (i = 0; i < exercise_comp_count() && n < EDIT_MAXITEMS; i++) {
        EditComp *c = exercise_comp(i);
        if (c && kind_has_phase(c->kind)) {
            char angle[20];
            idx[n] = i;
            strcpy(edit_item_buf[n], "Angulo: ");
            fmt_num(angle, cx_deg(c->value, c->value_im));
            strcat(edit_item_buf[n], angle); strcat(edit_item_buf[n], " deg");
            edit_item_ptrs[n] = edit_item_buf[n];
            n++;
        }
    }
    if (!n) return;
    wait_key_release();
    while (1) {
        check_on_exit(); kb_Scan();
        if (redraw) { draw_simple_list("Editar fases", edit_item_ptrs, n, selected); gfx_SwapDraw(); redraw = false; }
        if (pressed_once(kb_KeyClear)) { wait_key_release(); return; }
        if (pressed_once(kb_KeyDown) && selected + 1 < n) { selected++; redraw = true; }
        if (pressed_once(kb_KeyUp) && selected > 0) { selected--; redraw = true; }
        if (pressed_once(kb_KeyEnter)) {
            EditComp *c = exercise_comp(idx[selected]);
            char buf[16], hint[20];
            double mag = cx_mag(c->value, c->value_im), deg = cx_deg(c->value, c->value_im);
            fmt_num(hint, deg); input_line(buf, sizeof(buf), "Novo angulo (graus):", hint);
            if (buf[0]) {
                double rad = parse_float(buf) * 3.14159265358979323846 / 180.0;
                c->value = (float)(mag * cos(rad)); c->value_im = (float)(mag * sin(rad));
                exercise_apply_edit();
            }
            wait_key_release(); return;
        }
        delay(15);
    }
}

static void edit_frequency_once(void) {
    char buf[16], hint[20];
    fmt_eng(hint, exercise_frequency(), "rad/s");
    input_line(buf, sizeof(buf), "Nova frequencia w:", hint);
    if (buf[0]) exercise_set_frequency(parse_float(buf));
    wait_key_release();
}

static void edit_params_loop(void) {
    uint8_t n = exercise_param_count(), i, selected = 0;
    bool redraw = true;
    if (!n) return;
    for (i = 0; i < n; i++) {
        char value[20];
        const char *name = exercise_param_name(i);
        uint8_t pos = 0;
        while (name[pos] && pos < 12) {
            edit_item_buf[i][pos] = name[pos];
            pos++;
        }
        edit_item_buf[i][pos++] = ':';
        edit_item_buf[i][pos++] = ' ';
        edit_item_buf[i][pos] = 0;
        fmt_eng(value, exercise_param(i), ""); strcat(edit_item_buf[i], value);
        edit_item_ptrs[i] = edit_item_buf[i];
    }
    wait_key_release();
    while (1) {
        check_on_exit(); kb_Scan();
        if (redraw) { draw_simple_list("Editar parametros", edit_item_ptrs, n, selected); gfx_SwapDraw(); redraw = false; }
        if (pressed_once(kb_KeyClear)) { wait_key_release(); return; }
        if (pressed_once(kb_KeyDown) && selected + 1 < n) { selected++; redraw = true; }
        if (pressed_once(kb_KeyUp) && selected > 0) { selected--; redraw = true; }
        if (pressed_once(kb_KeyEnter)) {
            char buf[16], hint[20];
            fmt_eng(hint, exercise_param(selected), ""); input_line(buf, sizeof(buf), "Novo valor:", hint);
            if (buf[0]) exercise_set_param(selected, parse_float(buf));
            wait_key_release(); return;
        }
        delay(15);
    }
}

static void edit_menu_loop(void) {
    const char *items[5];
    uint8_t actions[5], count = 0;
    uint8_t selected = 0;
    bool redraw = true;

    if (exercise_comp_count()) { items[count] = "Editar magnitudes"; actions[count++] = 0; }
    if (exercise_is_ac() && exercise_comp_count()) { items[count] = "Editar fases"; actions[count++] = 1; }
    if (exercise_frequency() > 0.0f) { items[count] = "Editar frequencia"; actions[count++] = 2; }
    if (exercise_param_count()) { items[count] = "Editar parametros"; actions[count++] = 3; }
    if (exercise_comp_count()) { items[count] = "Direcoes/polaridade"; actions[count++] = 4; }
    if (!count) return;

    wait_key_release();
    while (1) {
        check_on_exit();
        kb_Scan();
        if (redraw) {
            draw_simple_list("Editar exercicio", items, count, selected);
            gfx_SwapDraw();
            redraw = false;
        }
        if (pressed_once(kb_KeyClear)) { wait_key_release(); return; }
        if (pressed_once(kb_KeyDown) && selected + 1 < count) { selected++; redraw = true; }
        if (pressed_once(kb_KeyUp) && selected > 0) { selected--; redraw = true; }
        if (pressed_once(kb_KeyEnter)) {
            wait_key_release();
            if (actions[selected] == 0) edit_values_menu_loop();
            else if (actions[selected] == 1) edit_phases_loop();
            else if (actions[selected] == 2) edit_frequency_once();
            else if (actions[selected] == 3) edit_params_loop();
            else edit_directions_loop();
            redraw = true;
        }
        delay(15);
    }
}

/* ---- subject/exercise viewer -------------------------------------------- */

static void subject_loop(uint8_t subject_index) {
    const SubRange *subject = &subjects[subject_index];
    uint16_t ex_index = 0;
    uint8_t page = 0;
    bool redraw = true;
    bool reload = true;             /* load from Flash only on navigation, */
    const Exercise *ex = 0;         /* NOT every frame - so RAM edits survive */
    uint16_t total = subject->count;

    if (!appvar_available()) {
        appvar_missing_loop();
        return;
    }

    wait_key_release();
    while (1) {
        if (reload) {
            ex = exercise_load((uint16_t)(subject->start + ex_index));
            if (!ex) {
                appvar_missing_loop();
                return;
            }
            reload = false;
        }

        check_on_exit();
        kb_Scan();

        if (redraw) {
            exercise_set_page(page);
            draw_ex_header(subject->title, ex->title, ex_index,
                           total, page, ex->page_count);
            draw_page_template(&ex->pages[page]);
            draw_footer_ex();
            gfx_SwapDraw();
            redraw = false;
        }

        if (pressed_once(kb_KeyClear)) {
            wait_key_release();
            return;
        }
        if (pressed_once(kb_KeyMode)) {
            wait_key_release();
            edit_menu_loop();
            /* edits mutate the loaded exercise in place (exercise_apply_edit
               already updated ex->page_count) - do NOT reload, that would
               discard the edit. Just clamp the page. */
            if (page >= ex->page_count) page = (uint8_t)(ex->page_count - 1);
            redraw = true;
        }
        if ((pressed_once(kb_KeyRight) || pressed_once(kb_KeyEnter)) &&
            page + 1 < ex->page_count) {
            page++;
            redraw = true;
        }
        if (pressed_once(kb_KeyLeft) && page > 0) {
            page--;
            redraw = true;
        }
        if (pressed_once(kb_KeyDown) && ex_index + 1 < total) {
            ex_index++;
            page = 0;
            reload = true;
            redraw = true;
        }
        if (pressed_once(kb_KeyUp) && ex_index > 0) {
            ex_index--;
            page = 0;
            reload = true;
            redraw = true;
        }
        delay(15);
    }
}

static void appvar_missing_loop(void) {
    bool redraw = true;

    wait_key_release();
    while (1) {
        check_on_exit();
        kb_Scan();
        if (redraw) {
            gfx_FillScreen(COL_WHITE);
            gfx_SetTextFGColor(COL_BLACK);
            print_center("CIRCVIE4", 8);
            gfx_SetColor(COL_BLACK);
            gfx_HorizLine(0, 24, SCREEN_W);
            print_center("Dados ausentes", 92);
            print_center("Envie CV4DAT0..N", 114);
            print_center("CLEAR volta", 140);
            draw_footer_ex();
            gfx_SwapDraw();
            redraw = false;
        }
        if (pressed_once(kb_KeyClear)) {
            wait_key_release();
            return;
        }
        delay(15);
    }
}

/* ---- component search ---------------------------------------------------- */

enum { SEARCH_BACK = 0, SEARCH_RUN = 1, SEARCH_SIN = 2, SEARCH_COS = 3 };

static void draw_search_select(const uint8_t counts[5], bool show_labels,
                               bool show_counts) {
    gfx_FillScreen(COL_WHITE);
    search_overlay_draw();
    draw_search_footer(counts, show_labels, show_counts);
}

static uint8_t search_select_loop(uint8_t counts[5]) {
    bool redraw = true;
    bool second = false;
    bool prev_alpha = false;
    bool prev_math = false;

    wait_key_release();
    while (1) {
        bool alpha_held, math_held;
        uint8_t hy, hw, hz, ht, hg;
        int comp;

        check_on_exit();
        kb_Scan();
        alpha_held = kb_IsDown(kb_KeyAlpha) ? true : false;
        math_held = kb_IsDown(kb_KeyMath) ? true : false;
        if (alpha_held != prev_alpha) { prev_alpha = alpha_held; redraw = true; }
        if (math_held != prev_math) { prev_math = math_held; redraw = true; }

        if (redraw) {
            draw_search_select(counts, alpha_held, math_held && !alpha_held);
            gfx_SwapDraw();
            redraw = false;
        }

        if (pressed_once(kb_Key2nd)) second = !second;

        hy = pressed_once(kb_KeyYequ);
        hw = pressed_once(kb_KeyWindow);
        hz = pressed_once(kb_KeyZoom);
        ht = pressed_once(kb_KeyTrace);
        hg = pressed_once(kb_KeyGraph);
        comp = hy ? 0 : hw ? 1 : hz ? 2 : ht ? 3 : hg ? 4 : -1;
        if (comp >= 0) {
            if (second) {
                if (counts[comp] > 0) counts[comp]--;
                second = false;
            } else if (counts[comp] < 99) {
                counts[comp]++;
            }
            redraw = true;
        }

        if (pressed_once(kb_KeySin)) { wait_key_release(); return SEARCH_SIN; }
        if (pressed_once(kb_KeyCos)) { wait_key_release(); return SEARCH_COS; }

        if (calc_handle_key()) redraw = true;

        if (pressed_once(kb_KeyEnter)) { wait_key_release(); return SEARCH_RUN; }
        if (pressed_once(kb_KeyClear)) {
            if (!calc_is_empty()) {
                calc_clear();
                redraw = true;
            } else {
                wait_key_release();
                return SEARCH_BACK;
            }
        }
        delay(15);
    }
}

static void search_no_match_loop(void) {
    bool redraw = true;
    wait_key_release();
    while (1) {
        check_on_exit();
        kb_Scan();
        if (redraw) {
            gfx_FillScreen(COL_WHITE);
            gfx_SetTextFGColor(COL_BLACK);
            print_center("Nenhum exercicio encontrado", 100);
            print_center("CLEAR volta", 120);
            draw_footer_ex();
            gfx_SwapDraw();
            redraw = false;
        }
        if (pressed_once(kb_KeyClear)) { wait_key_release(); return; }
        delay(15);
    }
}

static void search_results_loop(const uint16_t *filtered, uint16_t fcount) {
    uint16_t idx = 0;
    uint8_t page = 0;
    bool redraw = true;
    bool reload = true;             /* load only on navigation (see subject_loop) */
    bool big = fcount > 10;
    bool jump = false;
    const Exercise *ex = 0;
    const char *subject = 0;

    if (fcount == 0) { search_no_match_loop(); return; }

    wait_key_release();
    while (1) {
        if (reload) {
            uint16_t gidx = filtered[idx];
            subject = ex_meta[gidx].subject;
            ex = exercise_load(gidx);
            if (!ex) {
                appvar_missing_loop();
                return;
            }
            reload = false;
        }

        check_on_exit();
        kb_Scan();

        if (redraw) {
            exercise_set_page(page);
            draw_ex_header(subject, ex->title, idx, fcount,
                           page, ex->page_count);
            draw_page_template(&ex->pages[page]);
            draw_footer_ex();
            gfx_SwapDraw();
            redraw = false;
        }

        if (pressed_once(kb_KeyClear)) { wait_key_release(); return; }
        if (pressed_once(kb_KeyMode)) {
            wait_key_release();
            edit_menu_loop();
            if (page >= ex->page_count) page = (uint8_t)(ex->page_count - 1);
            redraw = true;
        }
        if ((pressed_once(kb_KeyRight) || pressed_once(kb_KeyEnter)) &&
            page + 1 < ex->page_count) { page++; redraw = true; }
        if (pressed_once(kb_KeyLeft) && page > 0) { page--; redraw = true; }

        if (big && pressed_once(kb_Key2nd)) jump = !jump;
        {
            bool dn = pressed_once(kb_KeyDown);
            bool up = pressed_once(kb_KeyUp);
            if (dn || up) {
                uint16_t old = idx;
                uint16_t step = (big && jump) ? 10 : 1;
                if (big) {
                    if (dn) idx = (uint16_t)((idx + step) % fcount);
                    else    idx = (uint16_t)((idx + fcount - (step % fcount)) % fcount);
                } else {
                    if (dn && idx + 1 < fcount) idx++;
                    else if (up && idx > 0) idx--;
                }
                jump = false;
                if (idx != old) { page = 0; reload = true; redraw = true; }
            }
        }
        delay(15);
    }
}

static void search_flow(void) {
    static uint8_t counts[5] = { 0, 0, 0, 0, 0 };
    static uint16_t filtered[256];
    const uint16_t cap = (uint16_t)(sizeof(filtered) / sizeof(filtered[0]));

    if (!appvar_available()) {
        appvar_missing_loop();
        return;
    }

    while (1) {
        uint8_t action = search_select_loop(counts);
        uint16_t i, fcount = 0;

        if (action == SEARCH_BACK) return;

        if (action == SEARCH_SIN || action == SEARCH_COS) {
            const uint16_t *src = (action == SEARCH_SIN) ? nofig_items : withfig_items;
            uint16_t n = (action == SEARCH_SIN) ? nofig_count : withfig_count;
            for (i = 0; i < n; i++) {
                if (fcount < cap) filtered[fcount++] = src[i];
            }
            search_results_loop(filtered, fcount);
            continue;
        }

        for (i = 0; i < ex_count; i++) {
            const ExMeta *m = &ex_meta[i];
            if (m->comp[0] >= counts[0] && m->comp[1] >= counts[1] &&
                m->comp[2] >= counts[2] && m->comp[3] >= counts[3] &&
                m->comp[4] >= counts[4]) {
                if (fcount < cap) {
                    filtered[fcount++] = i;
                }
            }
        }
        search_results_loop(filtered, fcount);
    }
}

int main(void) {
    kb_DisableOnLatch();
    kb_Scan();
    screen_init();
    calc_init();
    appvar_init();

    /* open straight into the search/calculator screen */
    search_flow();

    while (1) {
        int choice = main_menu_loop();
        const MenuItem *item;

        if (choice < 0) continue;
        item = &menu_items[choice];

        if (item->kind == MENU_SEARCH) {
            search_flow();
        } else {
            subject_loop(item->index);
        }
    }

    gfx_End();
    return 0;
}
