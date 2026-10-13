#ifndef CV4_LIVE_RECIPE_H
#define CV4_LIVE_RECIPE_H
#include "engine.h"
#define LIVE_MAXVARS 64
#define LIVE_STACK 24
typedef struct { float re, im; } LiveValue;
typedef struct {
    const EditComp *comps;
    uint8_t n_comps, n_nodes;
    const float *params;
    uint8_t n_params;
    float omega;
} LiveInputs;
/* Program stays in Flash. Only the bounded workspace and narration live in RAM. */
bool live_recipe_run(const uint8_t *program, uint16_t size,
                     const LiveInputs *inputs, Narration *out);
bool live_recipe_value(uint8_t index, LiveValue *out);
#endif
