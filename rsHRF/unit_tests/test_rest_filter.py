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


def test_Ideal_filter_adds_unique_column_means():
    matrix = np.ones((152, 3)) * np.array([10.0, 50.0, 100.0])
    m_expected = np.mean(matrix, axis=0)
    TR = 2.0
    filter = [0.01, 0.08]
    y = rest_filter.rest_IdealFilter(matrix, TR, filter)

    assert np.allclose(m_expected, np.mean(y, axis=0), rtol=1e-5)
