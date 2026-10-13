#include <math.h>
#include <stdio.h>
#include <string.h>

#include "engine.h"
#include "narrate_ac.h"

static int failures;

static EditComp comp(uint8_t kind, uint8_t na, uint8_t nb, float value) {
    EditComp c;
    memset(&c, 0, sizeof(c));
    c.kind = kind;
    c.na = na;
    c.nb = nb;
    c.ctrl = 0xFF;
    c.value = c.deflt = value;
    return c;
}

static void expect_ok(const char *name, const Narration *n) {
    if (n->impossible || n->count == 0) {
        printf("FAIL %s: %s\n", name,
               n->impossible ? n->impossible_reason : "sem passos");
        failures++;
    }
}

static int contains(const Narration *n, const char *needle) {
    uint8_t i;
    for (i = 0; i < n->count; i++)
        if (strstr(n->steps[i].text, needle)) return 1;
    return 0;
}

static void dump(const Narration *n) {
    uint8_t i;
    for (i = 0; i < n->count; i++) printf("  %s\n", n->steps[i].text);
}

static void test_worked_passive_routes(void) {
    Narration n;
    EditComp p957[] = {
        comp(CK_RES, 1, 2, 1.0f),
        comp(CK_IND, 2, 0, 2.0f),
        comp(CK_RES, 2, 3, 2.0f),
        comp(CK_CAP, 3, 0, 1.0f),
    };
    EditComp p962[] = {
        comp(CK_RES, 1, 3, 50.0f),
        comp(CK_IND, 3, 4, 0.002f),
        comp(CK_DVS, 4, 0, 100.0f),
        comp(CK_CAP, 2, 0, 0.000001f),
    };

    narrate_ac_impedance(p957, 4, 4, 1.0, 1, 0, &n);
    expect_ok("9.57 editavel", &n);
    if (!contains(&n, "Zeq = 2.6")) {
        puts("FAIL 9.57: impedancia recalculada ausente");
        dump(&n);
        failures++;
    }

    p962[2].ctrl = 0; /* fonte de 100 vezes a corrente no resistor */
    narrate_ac_impedance(p962, 4, 5, 10000.0, 1, 2, &n);
    expect_ok("9.62 editavel com fonte dependente", &n);
    if (!contains(&n, "Zeq = 150 - j80")) {
        puts("FAIL 9.62: impedancia recalculada ausente");
        dump(&n);
        failures++;
    }
}

static void test_source_value_and_polarity(void) {
    EditComp circuit[] = {
        comp(CK_VSRC, 1, 0, 10.0f),
        comp(CK_RES, 1, 0, 5.0f),
    };
    MnaTopology topo;
    MnaResult result;
    uint8_t elem_of[COMP_MAXN];

    topo.n_nodes = 2;
    build_mna_ac(circuit, 2, 1.0, &topo, elem_of);
    if (!mna_solve(&topo, &result) || fabs(result.node_v[1] - 10.0) > 1e-4) {
        puts("FAIL fonte: valor positivo");
        failures++;
    }

    circuit[0].value = 24.0f;
    circuit[0].flags ^= 1;
    build_mna_ac(circuit, 2, 1.0, &topo, elem_of);
    if (!mna_solve(&topo, &result) || fabs(result.node_v[1] + 24.0) > 1e-4) {
        puts("FAIL fonte: valor editado/polaridade invertida");
        failures++;
    }
}

int main(void) {
    EditComp tiny=comp(CK_CAP,1,0,1e-6f);
    edit_comp_set_magnitude(&tiny,10e-9f);
    if (fabs(tiny.value-10e-9f)>1e-14) { puts("FAIL editor clamps nanofarads"); failures++; }
    tiny=comp(CK_RES,1,0,10);
    edit_comp_set_magnitude(&tiny,0);
    if (tiny.value!=0) { puts("FAIL editor changes zero-ohm input"); failures++; }
    test_worked_passive_routes();
    test_source_value_and_polarity();
    if (failures) return 1;
    puts("EDITABLE ROUTES OK");
    return 0;
}
