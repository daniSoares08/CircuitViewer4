#ifndef CV4_NARRATE_POWER_H
#define CV4_NARRATE_POWER_H

#include "engine.h"

bool narrate_max_power(const float *params, uint8_t n, Narration *out);
bool narrate_three_phase(const float *params, uint8_t n, Narration *out);
bool narrate_power_profile(uint8_t profile, const float *params, uint8_t n,
                           Narration *out);
bool narrate_three_phase_profile(uint8_t profile, const float *params, uint8_t n,
                                 Narration *out);

enum {
    POWER_PROFILE_TRIANGLE = 1,
    POWER_PROFILE_LOAD_SUM = 2,
    POWER_PROFILE_PF_CORRECTION = 3,
    POWER_PROFILE_INSTANTANEOUS = 4
};

enum {
    THREE_PROFILE_DELTA_RELATION = 1,
    THREE_PROFILE_STAR_DELTA = 2,
    THREE_PROFILE_DELTA_STAR = 3,
    THREE_PROFILE_STAR_STAR = 4
};

#endif
