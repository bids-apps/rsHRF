import pytest
import numpy as np
from .. import parameters


def test_wgr_get_parameters():
    assert type(
        parameters.wgr_get_parameters(
            np.random.random(np.random.randint(1, 100)), np.random.uniform(0, 5)
        )
    ) == type(np.asarray([]))
    assert (
        parameters.wgr_get_parameters(
            np.random.random(np.random.randint(1, 100)), np.random.uniform(0, 5)
        ).size
        == 3
    )
    assert np.allclose(
        parameters.wgr_get_parameters(
            np.zeros(np.random.randint(1, 100)), np.random.uniform(0, 5)
        ),
        np.zeros(3),
    )
    dt = np.random.uniform(0, 5)
    assert np.allclose(
        parameters.wgr_get_parameters(np.ones(np.random.randint(100)), dt),
        np.asarray([1.0, dt, dt]),
    )
    assert np.allclose(
        parameters.wgr_get_parameters(
            np.asarray([0.54353434, 0.39763409, 0.92579636, 0.74797229, 0.89733085]),
            0.1,
        ),
        np.asarray([0.92579636, 0.3, 0.1]),
    )


def test_height_uses_plateau_start():
    """If the peak is at the end of a plateau, function will walk backwards and take the height value from the beginning of the plateau."""
    dt = 2.0
    vector = np.asarray(
        [0.0, 0.20, 0.60, 0.9000, 0.9003, 0.9005, 0.9010, 0.5, 0.2, -0.1, 0.0, 0.0]
    )
    result = parameters.wgr_get_parameters(vector, dt)
    expected = np.asarray([0.9, 8.0, 12.0])
    assert np.allclose(
        result, expected
    ), f"Height should come from the plateau start expected: {expected} got:{result}"
