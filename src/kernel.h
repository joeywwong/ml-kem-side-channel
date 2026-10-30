#ifndef LAB_KERNEL_H
#define LAB_KERNEL_H
#include <stdint.h>
#define LAB_Q 3329u
#if defined(__GNUC__) || defined(__clang__)
#define LAB_NOINLINE __attribute__((noinline))
#else
#define LAB_NOINLINE
#endif
/* Educational only. All coefficients must be canonical: 0 <= value < q.
 * No physical side-channel resistance is claimed. No allocation or RNG here. */
uint16_t lab_mul(uint16_t a, uint16_t s);
void lab_split(uint16_t s, uint16_t fresh_r, uint16_t shares[2]);
void lab_masked_mul(uint16_t a, const uint16_t shares[2], uint16_t out[2]);
uint16_t lab_recombine(const uint16_t out[2]);
#endif
