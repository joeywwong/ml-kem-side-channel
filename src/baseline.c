#include "kernel.h"
LAB_NOINLINE uint16_t lab_mul(uint16_t a, uint16_t s) {
    return (uint16_t)(((uint32_t)a * (uint32_t)s) % LAB_Q);
}
