import pytest
import numpy as np 
from rsHRF import iterative_wiener_deconv

def test_rsHRF_iterative_wiener_deconv():
    var1 = np.random.randint(100, 150)
    var2 = np.random.randint(4, 20)
    out = iterative_wiener_deconv.rsHRF_iterative_wiener_deconv(np.random.random(var1), np.random.random(var2))
    assert type(out) == type(np.asarray([]))
    assert out.size == var1
    y = np.asarray([0.6589422147608651, 0.7239697210706654, 0.5596745029686809, 0.1518281619871923, 0.9344253850406739, 0.06696275606106217, 0.8730982497140573, 0.22794714268930805, 0.6120490212897929])
    h = np.asarray([0.8401094233417159, 0.5039895222403991, 0.008901275117447982, 0.28477784598041767])
    out_expected = np.asarray([0.30156357, 0.30159647, 0.30155206, 0.30157723, 0.30157637, 0.30155563, 0.30159226, 0.30155481, 0.30159128])
    out = iterative_wiener_deconv.rsHRF_iterative_wiener_deconv(y, h)
    assert np.allclose(out, out_expected)