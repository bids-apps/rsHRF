import nibabel as nib
import numpy as np
from scipy import stats, linalg
from scipy.sparse import lil_matrix
from scipy.special import gammaln
from joblib import Parallel, delayed
from joblib import load, dump
import warnings
import math
import tempfile
import os
from rsHRF import canon, processing, spm_dep, sFIR, basis_functions
from ..processing import knee
warnings.filterwarnings("ignore")

"""
HRF ESTIMATION
"""

def compute_hrf(bold_sig, para, temporal_mask, p_jobs):
    para['temporal_mask'] = temporal_mask
    N, nvar = bold_sig.shape
    length = para['len']
    folder = tempfile.mkdtemp()
    data_folder = os.path.join(folder, 'data')
    dump(bold_sig, data_folder)
    data = load(data_folder, mmap_mode='r')

    results = Parallel(n_jobs=p_jobs)(delayed(estimate_hrf)(data, i, para, length,
                                  N) for i in range(nvar))

    beta_hrf, event_bold = zip(*results)

    try:
        shutil.rmtree(folder)
    except:
        print("Failed to delete: " + folder)

    return np.array(beta_hrf).T, np.array(event_bold)

def estimate_hrf(bold_sig, i, para, length, N):
    """
    Estimate HRF
    """
    dat = bold_sig[:, i]

    if 'localK' not in para:
        if para['TR']<=2:
            localK = 1
        else:
            localK = 2
    else:
        localK = para['localK']

    if para['estimation'] == 'sFIR' or para['estimation'] == 'FIR':
        para['T'] = 1
        #Estimate HRF for the sFIR or FIR basis functions
        if np.count_nonzero(para['thr']) == 1:
            para['thr'] = np.array([para['thr'], np.inf])
        thr = para['thr'] #Thr is a vector for (s)FIR
        u = wgr_BOLD_event_vector(N, dat, thr, localK, para['temporal_mask'])
        u = u.toarray().flatten(1).ravel().nonzero()[0]
        beta_hrf, event_bold = sFIR.smooth_fir.wgr_FIR_estimation_HRF(u, dat, para, N)
    else:
        #Estimate HRF for the fourier / hanning / gamma / cannon basis functions
        bf = basis_functions.basis_functions.get_basis_function(bold_sig, para)
        thr = [para['thr']] #Thr is a scalar for the basis functions
        u0 = wgr_BOLD_event_vector(N, dat, thr, localK, para['temporal_mask'])
        u = np.append(u0.toarray(), np.zeros((para['T'] - 1, N)), axis=0)
        u = np.reshape(u, (1, - 1), order='F')
        beta_hrf = wgr_hrf_fit(dat, length, para, u, N, bf)
        u = u0.toarray()[0].nonzero()[0]

    return beta_hrf, u

def wgr_onset_design(u, bf, T, T0, nscans):
    """
    @u - BOLD event vector (microtime).
    @bf - basis set matrix
    @T - microtime resolution (number of time bins per scan)
    @T0 - microtime onset (reference time bin, see slice timing)
    """
    ind = np.arange(0, max(u.shape))
    X = np.empty((0, len(ind)))
    for p in range(bf.shape[1]):
        x = np.convolve(u, bf[:, p])
        x = x[ind]
        X = np.append(X, [x], axis=0)
    X = X.T
    """
    Resample regressors at acquisition times
    """
    X = X[(np.arange(0, nscans) * T) + (T0 - 1), :]
    return X


def wgr_glm_estimation(dat, u, bf, T, T0, AR_lag):
    """
    @u - BOLD event vector (microtime).
    """
    nscans = dat.shape[0]
    x = wgr_onset_design(u, bf, T, T0, nscans)
    X = np.append(x, np.ones((nscans, 1)), axis=1)
    res_sum, Beta = sFIR.smooth_fir.wgr_glsco(X, dat, AR_lag)
    return np.real(res_sum), Beta

def wgr_hrf_fit(dat, length, xBF, u, N, bf):
    """
    @u    - BOLD event vector (microtime).
    @nlag - time lag from neural event to BOLD event
    """
    lag = xBF['lag']
    AR_lag = xBF['AR_lag']
    nlag = len(lag)
    erm = np.zeros((1, nlag))
    beta = np.zeros((bf.shape[1] + 1, nlag))
    for i in range(nlag):
        u_lag = np.append(u[0, lag[i]:], np.zeros((1, lag[i]))).T
        erm[0, i], beta[:, i] = \
            wgr_glm_estimation(dat, u_lag, bf, xBF['T'], xBF['T0'], AR_lag)

    x, idx = knee.knee_pt(np.ravel(erm))
    beta_hrf = beta[:, idx]
    beta_hrf = np.append(beta_hrf, lag[idx])
    return beta_hrf

def wgr_BOLD_event_vector(N, matrix, thr, k, temporal_mask):
    """
    Detect BOLD event.
    event > thr & event < 3.1
    """
    data = lil_matrix((1, N))
    matrix = matrix[:, np.newaxis]

    if 0 in np.array(temporal_mask).shape:
        matrix = stats.zscore(matrix, ddof=1)
        matrix = np.nan_to_num(matrix)
        for t in range(1 + k, N - k + 1):
            if matrix[t - 1, 0] > thr[0] and \
                    np.all(matrix[t - k - 1:t - 1, 0] < matrix[t - 1, 0]) and \
                    np.all(matrix[t - 1, 0] > matrix[t:t + k, 0]):
                data[0, t - 1] = 1
    else:
        datm = np.mean(matrix[temporal_mask])
        datstd = np.std(matrix[temporal_mask])
        datstd[datstd == 0] = 1
        matrix = np.divide((matrix - datm), datstd)
        for t in range(1 + k, N - k + 1):
            if temporal_mask[t-1]:
                if matrix[t - 1, 0] > thr[0] and \
                        np.all(matrix[t - k - 1:t - 1, 0] < matrix[t - 1, 0]) and \
                        np.all(matrix[t - 1, 0] > matrix[t:t + k, 0]):
                    data[0, t - 1] = 1
    return data
