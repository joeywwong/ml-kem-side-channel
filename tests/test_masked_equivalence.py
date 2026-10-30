import ctypes
import numpy as np
from test_reference_compatibility import library


def test_c_sharing_against_python():
    lib=library()
    rng=np.random.default_rng(600)
    shares=(ctypes.c_uint16*2)();out=(ctypes.c_uint16*2)()
    for a,s,r in rng.integers(0,3329,(10000,3)):
        a,s,r=int(a),int(s),int(r)
        lib.lab_split(s,r,shares)
        assert list(shares)==[r,(s-r)%3329]
        lib.lab_masked_mul(a,shares,out)
        assert list(out)==[a*r%3329,a*((s-r)%3329)%3329]
        assert lib.lab_recombine(out)==a*s%3329
