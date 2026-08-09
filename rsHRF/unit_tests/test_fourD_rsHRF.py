import os
from copy import deepcopy

import nibabel as nib
import numpy as np
from scipy.signal import convolve

from .. import fourD_rsHRF
from ..spm_dep import spm
from ..utils import hrf_estimation
from ..utils.default_parameters import default_parameters

TR = 2.0
X, Y, Z, nobs = 5, 6, 8, 30
# Voxels carrying signal, numbered in Fortran order. Chosen so that reading the
# same numbers in C order picks a disjoint set, which is what makes this test
# able to fail.
SIGNAL_VOXELS = [1, 83, 150, 192]
EVENT_ONSETS = [5, 15, 25]


def _write_bold(path):
    rng = np.random.default_rng(0)
    hrf = spm.spm_hrf(TR)
    neural = np.zeros(nobs)
    neural[EVENT_ONSETS] = 3.0
    signal = convolve(neural, hrf, mode="full")[:nobs]

    flat = np.zeros((X * Y * Z, nobs))
    flat[SIGNAL_VOXELS] = signal + rng.normal(0, 0.05, (len(SIGNAL_VOXELS), nobs))
    data = np.reshape(flat, (X, Y, Z, nobs), order="F")
    nib.save(nib.Nifti1Image(data, np.eye(4)), path)


def _para():
    para = deepcopy(default_parameters)
    para["TR"] = TR
    para["dt"] = para["TR"] / para["T"]
    para["lag"] = np.arange(
        np.trunc(para["min_onset_search"] / para["dt"]),
        np.trunc(para["max_onset_search"] / para["dt"]) + 1,
        dtype=int,
    )
    hrf_estimation.apply_localK_default(para)
    return para


def test_generated_mask_uses_fortran_order(tmp_path):
    """
    With no mask supplied, demo_rsHRF builds one from the temporal variance.
    That variance map has to be flattened the same way as the data itself
    (Fortran order); flattening it in C order makes voxel_ind point at
    different voxels than the ones that get extracted, so the analysis
    silently runs on the wrong voxels.
    """
    bold = str(tmp_path / "sub-01_task-rest_bold.nii")
    _write_bold(bold)
    out = str(tmp_path / "out")

    fourD_rsHRF.demo_rsHRF(bold, None, out, _para(), 1, file_type=".nii", mode="input")

    height = nib.load(os.path.join(out, "sub-01_task-rest_height.nii"))
    estimated = np.flatnonzero(height.get_fdata().flatten(order="F"))

    assert estimated.tolist() == SIGNAL_VOXELS
