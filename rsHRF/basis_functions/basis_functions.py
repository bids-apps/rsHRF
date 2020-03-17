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
BASIS FUNCTION COMPUTATION
"""

def get_basis_function(bold_sig, para):
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
        bf = canon2dd_bf(bold_sig, para)

    bf = spm_dep.spm.spm_orth(np.asarray(bf))
    return bf


def canon2dd_bf(data, xBF):
    """
    Returns canon basis functions
    """
    N, nvar = data.shape
    bf = canon.canon_hrf2dd.wgr_spm_get_canonhrf(xBF)
    bf2 = canon.canon_hrf2dd.wgr_spm_Volterra(bf, xBF)
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
