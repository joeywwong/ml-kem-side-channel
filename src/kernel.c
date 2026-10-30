#include "kernel.h"
/* Setup and recombination are deliberately separate from the proposed trigger.
 * A real device may leak here regardless of where the digital trigger is set. */
void lab_split(uint16_t s, uint16_t fresh_r, uint16_t shares[2]) {
    shares[0] = fresh_r;
    shares[1] = (uint16_t)(((uint32_t)s + LAB_Q - fresh_r) % LAB_Q);
}
uint16_t lab_recombine(const uint16_t out[2]) {
    return (uint16_t)(((uint32_t)out[0] + out[1]) % LAB_Q);
}
