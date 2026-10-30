#include "kernel.h"
#include <stdio.h>
#include <stdlib.h>
#define CHECK(c) do { if (!(c)) { fprintf(stderr,"FAIL line %d\n",__LINE__); return 1; } } while(0)
int main(void) {
    uint32_t a, s, r;
    uint16_t shares[2], out[2];
    /* Independent repeated-addition oracle for every canonical input pair. */
    for (a=0; a<LAB_Q; ++a) {
        uint32_t expected=0;
        for (s=0; s<LAB_Q; ++s) {
            CHECK(lab_mul((uint16_t)a,(uint16_t)s)==expected);
            expected += a;
            if (expected>=LAB_Q) expected-=LAB_Q;
        }
    }
    /* Every (s,r), varying a; plus all a for boundary secrets/masks below.
     * Not an exhaustive enumeration of all q^3 triples. */
    for (s=0; s<LAB_Q; ++s) for (r=0; r<LAB_Q; ++r) {
        a=(s*17u+r*31u)%LAB_Q;
        lab_split((uint16_t)s,(uint16_t)r,shares);
        CHECK(shares[0]<LAB_Q && shares[1]<LAB_Q);
        CHECK(((uint32_t)shares[0]+shares[1])%LAB_Q==s);
        lab_masked_mul((uint16_t)a,shares,out);
        CHECK(lab_recombine(out)==lab_mul((uint16_t)a,(uint16_t)s));
    }
    const uint16_t edges[]={0,1,1664,1665,3327,3328};
    for (a=0;a<LAB_Q;++a) for (s=0;s<6;++s) for(r=0;r<6;++r) {
        lab_split(edges[s],edges[r],shares);
        lab_masked_mul((uint16_t)a,shares,out);
        CHECK(lab_recombine(out)==lab_mul((uint16_t)a,edges[s]));
    }
    puts("PASS: 11082241 scalar pairs; 11082241 share pairs; 119844 boundary triples");
    return 0;
}
