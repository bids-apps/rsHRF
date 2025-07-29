import pytest
import numpy as np
from ..basis_functions import basis_functions

def test_fourier_bf():
    assert type(basis_functions.fourier_bf(np.random.random(5), {'estimation': 'fourier', 'order': 3})) == type(np.random.random(1))
    assert type(basis_functions.fourier_bf(np.random.random(5), {'estimation': 'fourier-hanning', 'order': 3})) == type(np.random.random(1))
    assert basis_functions.fourier_bf(np.random.random(5), {'estimation': 'fourier', 'order': 3}).shape == (5, 2*3 + 1)
    assert basis_functions.fourier_bf(np.random.random(5), {'estimation': 'fourier-hanning', 'order': 3}).shape == (5, 2*3 + 1)
    assert basis_functions.fourier_bf(np.random.random(15), {'estimation': 'fourier', 'order': 3}).shape == (15, 2*3 + 1)
    assert basis_functions.fourier_bf(np.random.random(15), {'estimation': 'fourier', 'order': 3}).shape == (15, 2*3 + 1)
    assert basis_functions.fourier_bf(np.random.random(7), {'estimation': 'fourier', 'order': 11}).shape == (7, 2*11 + 1)
    assert basis_functions.fourier_bf(np.random.random(7), {'estimation': 'fourier-hanning', 'order': 11}).shape == (7, 2*11 + 1)
    assert np.allclose(basis_functions.fourier_bf(np.zeros(5), {'estimation': 'fourier', 'order': 3}), np.asarray([[1, 0, 0, 0, 1, 1, 1] for i in range(5)]))
    assert np.allclose(basis_functions.fourier_bf(np.zeros(5), {'estimation': 'fourier-hanning', 'order': 3}), np.zeros((5, 2*3+1)))
    assert np.allclose(basis_functions.fourier_bf(np.ones(5), {'estimation': 'fourier', 'order': 3}), np.asarray([[1, 0, 0, 0, 1, 1, 1] for i in range(5)]))
    assert np.allclose(basis_functions.fourier_bf(np.ones(5), {'estimation': 'fourier-hanning', 'order': 3}), np.zeros((5, 2*3+1)))
    assert np.allclose(basis_functions.fourier_bf(np.full(5, np.pi/2), {'estimation': 'fourier', 'order': 3}), np.asarray([[ 1.,-0.43030122,0.77685322,-0.97220684,-0.90268536,0.62968173,-0.23412359] for i in range(5)]))
    assert np.allclose(basis_functions.fourier_bf(np.full(5, np.pi/2), {'estimation': 'fourier-hanning', 'order': 3}), np.asarray([[0.9513426809665357,-0.40936391340403033,0.7390536246669112,-0.9249018639367675,-0.8587631122906557,0.599043100699187,-0.222731764045654] for i in range(5)]))

def test_gamma_bf():
    assert type(basis_functions.gamma_bf(np.random.random(5), 7)) == type(np.random.random(1))
    assert basis_functions.gamma_bf(np.random.random(5), 7).shape == (5, 7)
    assert basis_functions.gamma_bf(np.random.random(6), 3).shape == (6, 3)
    assert basis_functions.gamma_bf(np.random.random(5), 17).shape == (5, 17)
    assert basis_functions.gamma_bf(np.random.random(15), 7).shape == (15, 7)
    assert basis_functions.gamma_bf(np.random.random(15), 11).shape == (15, 11)
    assert basis_functions.gamma_bf(np.random.random(15), 27).shape == (15, 27)
    assert np.allclose(basis_functions.gamma_bf(np.zeros(5), 7), np.zeros((5, 7)))
    assert np.allclose(basis_functions.gamma_bf(np.ones(5), 3), np.asarray([[6.13132402e-02, 7.29919526e-05, 2.81323432e-13] for i in range(5)]))