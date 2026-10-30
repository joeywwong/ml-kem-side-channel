#include "kernel.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#ifdef _WIN32
#include <windows.h>
static double now(void) { LARGE_INTEGER t,f; QueryPerformanceCounter(&t); QueryPerformanceFrequency(&f); return (double)t.QuadPart/(double)f.QuadPart; }
#else
#include <time.h>
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec+t.tv_nsec*1e-9; }
#endif
static uint16_t inputs[4096], shares[4096][2], secrets[4096];
static volatile uint32_t sink;
int main(int argc,char **argv) {
    if(argc!=2) return 2;
    /* Runtime-generated public benchmark fixtures, no security use of this LCG.
     * Preparation and mask generation excluded from timed intervals. */
    uint32_t state=(uint32_t)strtoul(argv[1],0,10);
    for(unsigned i=0;i<4096;++i) {
        state=state*1664525u+1013904223u; inputs[i]=(uint16_t)(state%3329);
        state=state*1664525u+1013904223u; secrets[i]=(uint16_t)(state%3329);
        state=state*1664525u+1013904223u; lab_split(secrets[i],(uint16_t)(state%3329),shares[i]);
    }
    puts("repeat,variant,iterations,seconds,checksum");
    for(unsigned rep=0;rep<10;++rep) for(unsigned order=0;order<2;++order) {
        unsigned variant=(rep+order)%2; /* alternate order to reduce drift bias */
        uint32_t checksum=0; uint16_t out[2];
        const unsigned iterations=10000000;
        double start=now();
        for(unsigned i=0;i<iterations;++i) {
            unsigned j=i&4095;
            if(variant) {
                lab_masked_mul(inputs[j],shares[j],out);
                checksum+=(uint32_t)out[0]+out[1];
            } else checksum+=lab_mul(inputs[j],secrets[j]);
        }
        double elapsed=now()-start;
        sink=checksum;
        printf("%u,%s,%u,%.9f,%u\n",rep,variant?"masked":"baseline",iterations,elapsed,checksum);
    }
    return 0;
}
