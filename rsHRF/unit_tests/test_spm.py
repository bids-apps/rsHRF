import pytest
from unittest import mock
import os
import math
import numpy   as np
import nibabel as nib
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
    if image_type == 'nifti':
        data = nib.Nifti1Image(data, np.eye(4))
    else:
        data = nib.gifti.GiftiDataArray(data.astype(np.float32), datatype='float32')
    return data

def test_spm_vol():
    test_file_1 = 'test.gii'
    test_file_2 = 'test.gii.gz'
    test_file_3 = 'test.nii'
    test_file_4 = 'test.nii.gz'
    test_files  = [test_file_1, test_file_2, test_file_3, test_file_4]
    with mock.patch('nibabel.load') as load_mock:
        for test_file in test_files:
            if 'nii' in test_file:
                load_mock.return_value = get_data('nifti')
            elif 'gii' in test_file:
                load_mock.return_value = get_data('gifti')
            v = spm.spm_vol(test_file)
            assert ('nii' in test_file or 'gii' in test_file)
            if 'nii' in test_file:
                assert type(v) == type(nib.Nifti1Image(np.asarray([]), np.eye(4)))
            elif 'gii' in test_file:
                assert isinstance(v, nib.gifti.GiftiDataArray)

def test_spm_read_vols():
    nifti = get_data('nifti')
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
    tests = [.5, 1, 2, 3, 4, 1.5, 2.5, 10]
    for test in tests:
        hrf = spm.spm_hrf(test)
        assert type(hrf) == type(np.asarray([]))
        assert len(hrf.shape) == 1
        assert hrf.size in [int(33/test) - 1, int(33/test), int(33/test) + 1] 

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
    test_file_1 = 'test.gii'
    test_file_2 = 'test.gii.gz'
    test_file_3 = 'test.nii'
    test_file_4 = 'test.nii.gz'
    test_files  = [test_file_1, test_file_2, test_file_3, test_file_4]
    with mock.patch('nibabel.load') as load_mock:
        for test_file in test_files:
            if 'nii' in test_file:
                load_mock.return_value = get_data('nifti')
            elif 'gii' in test_file:
                load_mock.return_value = get_data('gifti')
            v1 = spm.spm_vol(test_file)
            mask_data = np.zeros(SHAPE[:-1]).flatten(order='F').astype(np.float32)
            fname = test_file.split('.')[0]
            file_type = '.' + test_file.split('.', 1)[1]
            spm.spm_write_vol(v1, mask_data, fname, file_type)
            if 'gii' in file_type:
                file_type = '.gii'
            assert os.path.isfile(fname + file_type)
            os.remove(fname + file_type)