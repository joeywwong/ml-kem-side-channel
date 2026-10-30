/* Binary test adapter only; upstream remains unmodified. Never a network API. */
#include "kem.h"
#include "randombytes.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#ifdef _WIN32
#include <io.h>
#include <fcntl.h>
#endif
#define KP PQCLEAN_MLKEM512_CLEAN_crypto_kem_keypair
#define KPD PQCLEAN_MLKEM512_CLEAN_crypto_kem_keypair_derand
#define ENC PQCLEAN_MLKEM512_CLEAN_crypto_kem_enc
#define ENCD PQCLEAN_MLKEM512_CLEAN_crypto_kem_enc_derand
#define DEC PQCLEAN_MLKEM512_CLEAN_crypto_kem_dec
static int read_exact(uint8_t *p, size_t n) { return fread(p,1,n,stdin)==n; }
int main(int argc,char **argv) {
    uint8_t pk[800],sk[1632],ct[768],ss[32],dec[32],coins[64];
    if(argc!=2) return 2;
#ifdef _WIN32
    _setmode(_fileno(stdin),_O_BINARY); _setmode(_fileno(stdout),_O_BINARY);
#endif
    if(!strcmp(argv[1],"keygen")) {
        if(!read_exact(coins,64)||getchar()!=EOF) return 2;
        if(KPD(pk,sk,coins)) return 1;
        if(fwrite(pk,1,800,stdout)!=800||fwrite(sk,1,1632,stdout)!=1632) return 1;
    } else if(!strcmp(argv[1],"enc")) {
        if(!read_exact(pk,800)||!read_exact(coins,32)||getchar()!=EOF) return 2;
        if(ENCD(ct,ss,pk,coins)) return 1;
        if(fwrite(ct,1,768,stdout)!=768||fwrite(ss,1,32,stdout)!=32) return 1;
    } else if(!strcmp(argv[1],"dec")) {
        if(!read_exact(sk,1632)||!read_exact(ct,768)||getchar()!=EOF) return 2;
        if(DEC(ss,ct,sk)) return 1;
        if(fwrite(ss,1,32,stdout)!=32) return 1;
    } else if(!strcmp(argv[1],"smoke")) {
        for(unsigned i=0;i<100;++i) {
            if(KP(pk,sk)||ENC(ct,ss,pk)||DEC(dec,ct,sk)||memcmp(ss,dec,32)) return 1;
            ct[i%768]^=1;
            if(DEC(dec,ct,sk)||!memcmp(ss,dec,32)) return 1;
        }
        puts("PASS: 100 OS-randomized roundtrips and altered ciphertexts");
    } else return 2;
    return 0;
}
