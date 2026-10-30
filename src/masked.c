#include "kernel.h"
LAB_NOINLINE void lab_masked_mul(uint16_t a, const uint16_t shares[2], uint16_t out[2]) {
    out[0] = lab_mul(a, shares[0]);
    out[1] = lab_mul(a, shares[1]);
}
