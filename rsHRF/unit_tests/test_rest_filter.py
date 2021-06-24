import pytest
import numpy as np 
from ..processing import rest_filter 

def test_conn_filter():
    TR = np.random.randint(1, 10)
    filter = [0.01, 0.08]
    x = np.zeros((152, 1))
    y = rest_filter.conn_filter(TR, filter, x)
    assert type(y) == type(np.asarray([]))
    assert y.shape == (152, 1)
    assert np.allclose(y, np.zeros((152, 1)))
    x = np.ones((152, 1))
    y = rest_filter.conn_filter(TR, filter, x)
    assert np.allclose(y, np.zeros((152, 1)))

def test_rest_IdealFilter():
    TR = 2.0
    filter = [0.01, 0.08]
    x = np.zeros((152, 1))
    y = rest_filter.rest_IdealFilter(x, TR, filter)
    assert type(y) == type(np.asarray([]))
    assert y.shape == (152, 1)
    assert np.allclose(y, np.zeros((152, 1)))
    x = np.ones((152, 1))
    y = rest_filter.rest_IdealFilter(x, TR, filter)
    assert np.allclose(y, np.ones((152, 1)))