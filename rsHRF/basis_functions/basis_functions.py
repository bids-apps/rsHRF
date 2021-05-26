import math
import numpy as np
from scipy.stats import gamma
from rsHRF import canon, spm_dep, sFIR

import warnings
warnings.filterwarnings("ignore")

"""
BASIS FUNCTION COMPUTATION
"""

def get_basis_function(bold_sig_shape, para):
    N, nvar = bold_sig_shape
    dt = para['dt'] # 'time bin for basis functions {secs}';
    l  = para['len']
    if "gamma" in para['estimation']:
        pst = np.arange(0,l+0.01,dt) #the 0.01 is because the rounding is different between python and matlab
        bf  = gamma_bf(pst,para['order'])
    elif 'fourier' in para['estimation'] or 'hanning' in para['estimation']:
        pst = np.arange(0,l+0.01,dt) #the 0.01 is because the rounding is different between python and matlab
        pst = pst/max(pst)
        bf  = fourier_bf(pst,para)
    elif 'canon' in para['estimation']:
        bf = canon2dd_bf(bold_sig_shape, para)
    bf = spm_dep.spm.spm_orth(np.asarray(bf))
    return bf

def canon2dd_bf(data_shape, xBF):
    """
    Returns canon basis functions
    """
    N, nvar = data_shape
    bf = canon.canon_hrf2dd.wgr_spm_get_canonhrf(xBF)
    if 'Volterra' in xBF:
        if xBF['Volterra'] == 2:
            bf2 = np.einsum('i...,j...->ij...',bf.T,bf.T).reshape(-1, bf.shape[0]).T
            bf  = np.column_stack((bf, bf2))
    return bf

def fourier_bf(pst,para):
    """
    Returns Fourier (Hanning) basis functions
    """
    if "hanning" in para['estimation']:
        g = (1 - np.cos(2*math.pi*pst)) / 2
    else:
        g = np.ones(len(pst))
    sin_ = lambda x : np.sin(x*2*math.pi)
    cos_ = lambda x : np.cos(x*2*math.pi) 
    sin_ = np.vectorize(sin_)
    cos_ = np.vectorize(cos_)
    arr = np.arange(1, para['order']+1)
    s = sin_(np.einsum('i,j->ij',arr,pst))
    c = cos_(np.einsum('i,j->ij',arr,pst))
    s = np.multiply(g,s)
    c = np.multiply(g,c)
    g = np.expand_dims(g, axis=1).T
    return np.concatenate((g, s, c), axis=0).T

def gamma_bf(u,h):
    """
    Returns Gamma basis functions
    """
    arr = np.arange(2, h+2)
    f = np.vectorize(gamma.pdf, signature='(n),()->(n)')
    m = np.power(2, arr)
    return f(u,m).T

