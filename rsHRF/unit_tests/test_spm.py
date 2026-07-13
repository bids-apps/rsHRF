import pytest
from unittest import mock
import os
import math
import numpy as np
import nibabel as nib
from scipy import signal
from scipy.special import gammaln
from ..spm_dep import spm

SHAPE = (10, 10, 10, 10)


def get_data(image_type):
    data = np.array(np.random.random(SHAPE), dtype=np.float32)
    mask = np.random.random(SHAPE[:3]) > 0.1
    if len(SHAPE) > 3:
        data[mask, :] = 0
    else:
        data[mask] = 0
    if image_type == "nifti":
        data = nib.Nifti1Image(data, np.eye(4))
    else:
        data = nib.gifti.GiftiDataArray(data.astype(np.float32), datatype="float32")
    return data


def test_spm_vol():
    test_file_1 = "test.gii"
    test_file_2 = "test.gii.gz"
    test_file_3 = "test.nii"
    test_file_4 = "test.nii.gz"
    test_files = [test_file_1, test_file_2, test_file_3, test_file_4]
    with mock.patch("nibabel.load") as load_mock:
        for test_file in test_files:
            if "nii" in test_file:
                load_mock.return_value = get_data("nifti")
            elif "gii" in test_file:
                load_mock.return_value = get_data("gifti")
            v = spm.spm_vol(test_file)
            assert "nii" in test_file or "gii" in test_file
            if "nii" in test_file:
                assert type(v) == type(nib.Nifti1Image(np.asarray([]), np.eye(4)))
            elif "gii" in test_file:
                assert isinstance(v, nib.gifti.GiftiDataArray)


def test_spm_read_vols():
    nifti = get_data("nifti")
    data = spm.spm_read_vols(nifti)
    assert type(data) == type(np.asarray([]))
    assert data.shape[0] == pow(10, 4)


def test_spm_orth():
    tests = [(3, 4), (7, 5), (4, 12), (13, 6), (11, 11)]
    for test in tests:
        X = np.random.random(test)
        Y = spm.spm_orth(X)
        assert type(Y) == type(X)
        assert Y.shape == X.shape


def test_spm_hrf():
    tests = [0.5, 1, 2, 3, 4, 1.5, 2.5, 10]
    for test in tests:
        hrf = spm.spm_hrf(test)
        assert type(hrf) == type(np.asarray([]))
        assert len(hrf.shape) == 1
        assert hrf.size in [int(33 / test) - 1, int(33 / test), int(33 / test) + 1]


def test_spm_detrend():
    tests = [(3, 4), (7, 5), (4, 12), (13, 6), (11, 11)]
    for test in tests:
        X = np.random.random(test)
        Y = spm.spm_detrend(X)
        assert type(Y) == type(X)
        assert Y.shape == X.shape
        Y = Y.T
        Y_sum = np.sum(Y, axis=1)
        assert np.allclose(Y_sum, np.zeros(Y_sum.shape))


def test_spm_write_vol():
    test_file_1 = "test.gii"
    test_file_2 = "test.gii.gz"
    test_file_3 = "test.nii"
    test_file_4 = "test.nii.gz"
    test_files = [test_file_1, test_file_2, test_file_3, test_file_4]
    with mock.patch("nibabel.load") as load_mock:
        for test_file in test_files:
            if "nii" in test_file:
                load_mock.return_value = get_data("nifti")
            elif "gii" in test_file:
                load_mock.return_value = get_data("gifti")
            v1 = spm.spm_vol(test_file)
            mask_data = np.zeros(SHAPE[:-1]).flatten(order="F").astype(np.float32)
            fname = test_file.split(".")[0]
            file_type = "." + test_file.split(".", 1)[1]
            spm.spm_write_vol(v1, mask_data, fname, file_type)
            if "gii" in file_type:
                file_type = ".gii"
            assert os.path.isfile(fname + file_type)
            os.remove(fname + file_type)


def test_spm_detrend_matches_scipy_for_linear_order():
    """Independent reference: scipy removes a least-squares line for p = 1."""
    rng = np.random.default_rng(3)
    x = rng.standard_normal((30, 4)) + np.linspace(0, 5, 30)[:, None]
    assert np.allclose(spm.spm_detrend(x, 1), signal.detrend(x, axis=0, type="linear"))


def test_spm_detrend_removes_trend_and_keeps_the_rest():
    """p > 0 was unreachable: d.flatten(1) raised TypeError on modern NumPy."""
    m = 24
    t = np.arange(1, m + 1)
    for p in (1, 2, 3):
        trend = np.polyval(
            np.polyfit(t, 3.0 - 0.4 * t + 0.02 * t**2 - 0.0005 * t**3, p), t
        )
        osc = np.sin(2 * np.pi * t / 6.0)
        x = np.column_stack([trend + osc, trend - osc])

        y = spm.spm_detrend(x, p)
        assert y.shape == x.shape

        # the polynomial trend is gone
        G = np.column_stack([t**i for i in range(p + 1)]).astype(float)
        assert np.allclose(np.linalg.pinv(G) @ y, 0.0, atol=1e-8)

        # but the oscillation survives: an implementation that returns zeros fails here
        assert np.abs(y).max() > 0.5


def test_spm_detrend_order_zero_equals_mean_projection():
    """The `if not p` shortcut must equal projecting out a constant column."""
    rng = np.random.default_rng(0)
    x = rng.standard_normal((15, 4))
    G = np.ones((15, 1))
    assert np.allclose(spm.spm_detrend(x, 0), x - G @ np.linalg.pinv(G) @ x)
