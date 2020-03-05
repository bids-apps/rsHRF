import numpy as np
from joblib import Parallel, delayed
from joblib import load, dump
import tempfile
import shutil
import os
import warnings
from ..spm_dep import spm
from ..processing import knee

warnings.filterwarnings("ignore")


def wgr_spm_Volterra(bf, xBF):
    bf2 = []
    if 'Volterra' in xBF:
        if xBF['Volterra'] == 2:
            bf2 = []
            for p in range(bf.shape[1]):
                for q in range(bf.shape[1]):
                    bf2.append((bf[:, p] * bf[:, q]))
            bf2 = np.array(bf2).T
            bf2 = spm.spm_orth(bf2)
    return bf2


def wgr_spm_get_canonhrf(xBF):
    dt = xBF['dt']
    fMRI_T = xBF['T']

    bf = spm.spm_hrf(dt, P=None, fMRI_T=fMRI_T)
    p = np.array([6, 16, 1, 1, 6, 0, 32], dtype=float)
    p[len(p) - 1] = xBF['len']

    bf = spm.spm_hrf(dt, p, fMRI_T)
    bf = bf[:, np.newaxis]

    if xBF['TD_DD']:
        dp = 1
        p[5] = p[5] + dp
        D = (bf[:, 0] - spm.spm_hrf(dt, p, fMRI_T)) / dp
        D = D[:, np.newaxis]
        bf = np.append(bf, D, axis=1)
        p[5] = p[5] - dp
        if xBF['TD_DD'] == 2:
            dp = 0.01
            p[2] = p[2] + dp
            D = (bf[:, 0] - spm.spm_hrf(dt, p, fMRI_T)) / dp
            D = D[:, np.newaxis]
            bf = np.append(bf, D, axis=1)

    bf = spm.spm_orth(bf)
    return bf
