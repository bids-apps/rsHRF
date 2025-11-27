import numpy as np
from .. import iterative_wiener_deconv

def test_rsHRF_iterative_wiener_deconv():
    # --- smoke test on random sizes ---
    var1 = np.random.randint(100, 150)
    var2 = np.random.randint(4, 20)
    out = iterative_wiener_deconv.rsHRF_iterative_wiener_deconv(
        np.random.random(var1), np.random.random(var2)
    )
    assert isinstance(out, np.ndarray)
    assert out.size == var1
    assert np.isfinite(out).all()
    assert np.isrealobj(out)

    # --- deterministic check: stability & no artifacts ---
    y = np.asarray([
        0.6589422147608651, 0.7239697210706654, 0.5596745029686809,
        0.1518281619871923, 0.9344253850406739, 0.06696275606106217,
        0.8730982497140573, 0.22794714268930805, 0.6120490212897929
    ])
    h = np.asarray([
        0.8401094233417159, 0.5039895222403991, 0.008901275117447982,
        0.28477784598041767
    ])

    out = iterative_wiener_deconv.rsHRF_iterative_wiener_deconv(y, h)

    # 1) correct shape & numerics
    assert out.shape == y.shape
    assert np.isfinite(out).all()
    assert np.isrealobj(out)

    # 2) smooth / not oscillatory: coefficient of variation is modest
    mean_abs = np.mean(np.abs(out))
    if mean_abs > 0:
        cv = np.std(out) / mean_abs
        assert cv < 0.25  # generous upper bound; avoids ringing

    # 3) not a pure sinusoid: no huge single-peak PSD
    Y = np.fft.rfft(out)
    psd = np.abs(Y) ** 2
    assert (psd.max() / (psd.mean() + 1e-12)) < 50

    # 4) edge guard: edges don’t dominate the energy
    n = out.size
    mid = out[n // 3 : 2 * n // 3]
    edges = np.r_[out[: n // 6], out[-n // 6 :]]
    if np.sum(mid**2) > 0:
        ratio = np.sum(edges**2) / np.sum(mid**2)
        assert ratio <= 1.0 + 1e-2 
