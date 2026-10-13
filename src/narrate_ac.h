/* CircuitViewer4 - github.com/daniSoares08
 * Open source (MIT License): free to use, copy, modify and redistribute. */
#ifndef CV4_NARRATE_AC_H
#define CV4_NARRATE_AC_H

#include "engine.h"

/* Phasor-domain narrators (book chapters 9-10). Every one of these takes
 * `omega` in rad/s and reads each component's PHYSICAL value - farads and
 * henries, not impedances - so editing either a component or the frequency
 * changes the answer, which is the whole point of the live-circuit design.
 *
 * Portable/testable exactly like narrate.c: no calculator headers. */

/* Impedance table: one line per reactive element showing R / jwL / -j/(wC)
 * both ways round, then the node voltages in polar form. This is the AC
 * counterpart of narrate_nodal() and covers "analise nodal AC". */
bool narrate_ac_nodal(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                      double omega, const char *const *node_label, uint8_t target,
                      bool target_voltage,
                      Narration *out);

/* Equivalent impedance seen between port_a and port_b, by injecting a 1/_0 A
 * test source with every independent source zeroed - the same trick
 * narrate_thevenin() uses for Rth, which works unchanged in the complex
 * domain. Reports Z in rectangular and polar form, and Y = 1/Z. */
bool narrate_ac_impedance(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                          double omega, uint8_t port_a, uint8_t port_b,
                          Narration *out);

bool narrate_ac_mesh(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                     double omega, const MeshEdge *const *meshes,
                     const uint8_t *mesh_len, uint8_t n_meshes,
                     uint8_t target,
                     Narration *out);
bool narrate_ac_superposition(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                              double omega, uint8_t target, Narration *out);
bool narrate_ac_thevenin(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                         double omega, uint8_t port_a, uint8_t port_b,
                         Narration *out);
bool narrate_ac_power(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                      double omega, uint8_t target, bool peak, bool delivered,
                      Narration *out);
bool narrate_ac_power_factor(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                             double omega, uint8_t port_a, uint8_t port_b,
                             Narration *out);
bool narrate_ac_max_power(const EditComp *comps, uint8_t n, uint8_t n_nodes,
                          double omega, uint8_t port_a, uint8_t port_b,
                          bool peak, Narration *out);

#endif
