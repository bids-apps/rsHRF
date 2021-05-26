import os
import shutil
import tempfile
import numpy as np
from scipy        import stats
from scipy.sparse import lil_matrix
from joblib       import load, dump
from joblib       import Parallel, delayed
from rsHRF        import processing, sFIR
from ..processing import knee

import warnings
warnings.filterwarnings("ignore")

"""
HRF ESTIMATION
"""

def compute_hrf(bold_sig, para, temporal_mask, p_jobs, bf = None):
    para['temporal_mask'] = temporal_mask
    N, nvar = bold_sig.shape
    folder = tempfile.mkdtemp()
    data_folder = os.path.join(folder, 'data')
    dump(bold_sig, data_folder)
    data = load(data_folder, mmap_mode='r')
    results = Parallel(n_jobs=p_jobs)(delayed(estimate_hrf)(data, i, para,
                                  N, bf) for i in range(nvar))
    beta_hrf, event_bold = zip(*results)
    try:
        shutil.rmtree(folder)
    except:
        print("Failed to delete: " + folder)
    return np.array(beta_hrf).T, np.array(event_bold)

def estimate_hrf(bold_sig, i, para, N, bf = None):
    """
    Estimate HRF
    """
    dat = bold_sig[:, i]
    localK = para['localK']
    if para['estimation'] == 'sFIR' or para['estimation'] == 'FIR':
        #Estimate HRF for the sFIR or FIR basis functions
        if np.count_nonzero(para['thr']) == 1:
            para['thr'] = np.array([para['thr'], np.inf])
        thr = para['thr'] #Thr is a vector for (s)FIR
        u = wgr_BOLD_event_vector(N, dat, thr, localK, para['temporal_mask'])
        u = u.toarray().flatten('C').ravel().nonzero()[0]
        beta_hrf, event_bold = sFIR.smooth_fir.wgr_FIR_estimation_HRF(u, dat, para, N)
    else:
        thr = [para['thr']] #Thr is a scalar for the basis functions
        u0 = wgr_BOLD_event_vector(N, dat, thr, localK, para['temporal_mask'])
        u = np.append(u0.toarray(), np.zeros((para['T'] - 1, N)), axis=0)
        u = np.reshape(u, (1, - 1), order='F')
        beta_hrf = wgr_hrf_fit(dat, para, u, bf)
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
    res_sum, Beta = sFIR.smooth_fir.wgr_glsco(X, dat, AR_lag=AR_lag)
    return np.real(res_sum), Beta

def wgr_hrf_fit(dat, xBF, u, bf):
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
    if idx == nlag-1:
        idx = idx - 1
    beta_hrf = beta[:, idx+1]
    beta_hrf = np.append(beta_hrf, lag[idx+1])
    return beta_hrf

def wgr_BOLD_event_vector(N, matrix, thr, k, temporal_mask):
    """
    Detect BOLD event.
    event > thr & event < 3.1
    """
    data = lil_matrix((1, N))
    matrix = matrix[:, np.newaxis]
    matrix = np.nan_to_num(matrix)
    if 0 in np.array(temporal_mask).shape:
        matrix = stats.zscore(matrix, ddof=1)
        for t in range(1 + k, N - k + 1):
            if matrix[t - 1, 0] > thr[0] and \
                    np.all(matrix[t - k - 1:t - 1, 0] < matrix[t - 1, 0]) and \
                    np.all(matrix[t - 1, 0] > matrix[t:t + k, 0]):
                data[0, t - 1] = 1
    else:
        tmp = temporal_mask
        for i in range(len(temporal_mask)):
            if tmp[i] == 1:
                temporal_mask[i] = i
        datm = np.mean(matrix[temporal_mask])
        datstd = np.std(matrix[temporal_mask])
        if datstd == 0: datstd = 1
        matrix = (matrix - datm)/datstd
        for t in range(1 + k, N - k + 1):
            if tmp[t-1]:
                if matrix[t - 1, 0] > thr[0] and \
                        np.all(matrix[t - k - 1:t - 1, 0] < matrix[t - 1, 0]) and \
                        np.all(matrix[t - 1, 0] > matrix[t:t + k, 0]):
                    data[0, t - 1] = 1.
    return data
