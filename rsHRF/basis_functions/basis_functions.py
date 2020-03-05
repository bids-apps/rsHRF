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
from rsHRF import canon, processing, spm_dep, sFIR
from ..processing import knee
warnings.filterwarnings("ignore")

"""
HRF ESTIMATION
"""
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
    return beta[:, idx], lag[idx]

def wgr_estimate_hrf(data, i, xBF, length, N, bf, temporal_mask):
    """
    Estimate HRF
    """
    dat = data[:, i]
    thr = xBF['thr']

    if 'localK' not in xBF:
        if xBF['TR']<=2:
            localK = 1
        else:
            localK = 2
    else:
        localK = xBF['localK']
    u0 = wgr_BOLD_event_vector(N, dat, thr, localK, temporal_mask)
    u = np.append(u0.toarray(), np.zeros((xBF['T'] - 1, N)), axis=0)
    u = np.reshape(u, (1, - 1), order='F')
    beta, lag = wgr_hrf_fit(dat, length, xBF, u, N, bf)
    beta_hrf = beta
    beta_hrf = np.append(beta_hrf, lag)
    return beta_hrf, u0.toarray()[0].nonzero()[0]


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
            if matrix[t - 1, 0] > thr and \
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
                if matrix[t - 1, 0] > thr and \
                        np.all(matrix[t - k - 1:t - 1, 0] < matrix[t - 1, 0]) and \
                        np.all(matrix[t - 1, 0] > matrix[t:t + k, 0]):
                    data[0, t - 1] = 1
    return data

"""
BASIS FUNCTION COMPUTATION
"""


def compute_basis_function(bold_sig, para, temporal_mask, p_jobs):
    N, nvar = bold_sig.shape

    bf = get_basis_function(bold_sig, para, temporal_mask, p_jobs)
    length = para['len']
    folder = tempfile.mkdtemp()
    data_folder = os.path.join(folder, 'data')
    dump(bold_sig, data_folder)

    data = load(data_folder, mmap_mode='r')
    
    results = Parallel(n_jobs=p_jobs)(delayed(wgr_estimate_hrf)(data, i, para, length,
                                  N, bf, temporal_mask) for i in range(nvar))

    beta_hrf, event_bold = zip(*results)

    try:
        shutil.rmtree(folder)
    except:
        print("Failed to delete: " + folder)

    return np.array(beta_hrf).T, bf, np.array(event_bold)


def get_basis_function(bold_sig, para, temporal_mask, p_jobs):
    N, nvar = bold_sig.shape
    dt = para['dt'] # 'time bin for basis functions {secs}';
    l  = para['len']

    if "gamma" in para['estimation']:
        pst = np.arange(0,l+0.01,dt) #the 0.01 is because the rounding is different between python and matlab
        bf = gamma_bf(pst,para['order'])
    elif 'fourier' in para['estimation'] or 'hanning' in para['estimation']:
        pst = np.arange(0,l,dt)
        pst = pst/max(pst)
        bf = fourier_bf(pst,para)
    elif 'canon' in para['estimation']:
        bf = canon2dd_bf(data, para)

    bf = spm_dep.spm.spm_orth(np.asarray(bf))
    return bf


def canon2dd_bf(data, xBF):
    """
    Returns canon basis functions
    """
    N, nvar = data.shape
    bf = wgr_spm_get_canonhrf(xBF)
    bf2 = wgr_spm_Volterra(bf, xBF)
    if bf2 != []:
        bf = np.column_stack((bf, bf2))
    return bf

def fourier_bf(pst,para):
    """
    Returns Fourier (Hanning) basis functions
    """
    if "hanning" in para['estimation']:
        g = (1 - np.cos(2*math.pi*pst)) / 2
    else:
        g = np.ones(len(pst))

    bf = [g];
    for i in range(1,para['order']+1):
        bf.append(np.multiply(g, np.sin(i*2*math.pi*pst)))
        bf.append(np.multiply(g, np.cos(i*2*math.pi*pst)))

    return np.array(bf).transpose()

def gamma_bf(u,h):
    """
    Returns Gamma basis functions
    """
    _spm_Gpdf = lambda x, h, l: \
        np.exp(h * np.log(l) + (h - 1) * np.log(x) - (l * x) - gammaln(h))
    bf    = []
    for i in range(2,  h + 2):
        m   = np.power(2, i)
        s   = np.sqrt(m)
        bf.append(_spm_Gpdf(u,np.power((m/s),2),m/np.power(s,2)))
    return np.array(bf).transpose()
