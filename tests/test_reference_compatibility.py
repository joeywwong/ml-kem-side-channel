import ctypes
from functools import lru_cache
import os
from pathlib import Path
import numpy as np
from common import ROOT,BUILD,PQ,compile_c,kernel_sources,verify_sources


@lru_cache(maxsize=1)
def library():
    verify_sources()
    flags=['-shared']+([] if os.name=='nt' else ['-fPIC'])
    path=compile_c('arithmetic',kernel_sources()+[PQ/'reduce.c'],[ROOT/'src',PQ],flags)
    lib=ctypes.CDLL(str(path))
    lib.lab_mul.argtypes=[ctypes.c_uint16,ctypes.c_uint16]
    lib.lab_mul.restype=ctypes.c_uint16
    red=lib.PQCLEAN_MLKEM512_CLEAN_montgomery_reduce
    red.argtypes=[ctypes.c_int32];red.restype=ctypes.c_int16
    lib.lab_split.argtypes=[ctypes.c_uint16,ctypes.c_uint16,ctypes.POINTER(ctypes.c_uint16)]
    lib.lab_masked_mul.argtypes=[ctypes.c_uint16,ctypes.POINTER(ctypes.c_uint16),ctypes.POINTER(ctypes.c_uint16)]
    lib.lab_recombine.argtypes=[ctypes.POINTER(ctypes.c_uint16)]
    lib.lab_recombine.restype=ctypes.c_uint16
    return lib


def test_scalar_relation_to_upstream_montgomery():
    lib=library()
    rng=np.random.default_rng(500)
    pairs=[(a,s) for a in [0,1,1664,3328] for s in range(3329)]
    pairs+=list(rng.integers(0,3329,(5000,2)))
    for a,s in pairs:
        a,s=int(a),int(s)
        got=lib.lab_mul(a,s)
        assert got==a*s%3329
        # Montgomery output is NOT the canonical scalar output without conversion.
        reduced=lib.PQCLEAN_MLKEM512_CLEAN_montgomery_reduce(a*s)
        assert (reduced*65536)%3329==got
