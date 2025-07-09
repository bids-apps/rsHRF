import pytest
import numpy as np 
from .. import iterative_wiener_deconv

def test_rsHRF_iterative_wiener_deconv():
    var1 = np.random.randint(100, 150)
    var2 = np.random.randint(4, 20)
    out = iterative_wiener_deconv.rsHRF_iterative_wiener_deconv(np.random.random(var1), np.random.random(var2))
    assert type(out) == type(np.asarray([]))
    assert out.size == var1
    y = np.asarray([0.6589422147608651, 0.7239697210706654, 0.5596745029686809, 0.1518281619871923, 0.9344253850406739, 0.06696275606106217, 0.8730982497140573, 0.22794714268930805, 0.6120490212897929])
    h = np.asarray([0.8401094233417159, 0.5039895222403991, 0.008901275117447982, 0.28477784598041767])
    out_expected = np.asarray([0.02218669, 0.02221875, 0.02217417, 0.02219945, 0.02219854, 0.02217766, 0.02221443, 0.02217762, 0.02221311])
    out = iterative_wiener_deconv.rsHRF_iterative_wiener_deconv(y, h)
    assert np.allclose(out, out_expected)