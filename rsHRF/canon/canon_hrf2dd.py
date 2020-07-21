import numpy as np
from ..spm_dep    import spm
from ..processing import knee

import warnings
warnings.filterwarnings("ignore")

def wgr_spm_get_canonhrf(xBF):
    dt     = xBF['dt']
    fMRI_T = xBF['T']
    p      = np.array([6, 16, 1, 1, 6, 0, 32], dtype=float)
    p[len(p) - 1] = xBF['len']
    bf = spm.spm_hrf(dt, p, fMRI_T)
    bf = bf[:, np.newaxis]
    # time-derivative
    if xBF['TD_DD']:
        dp   = 1
        p[5] = p[5] + dp
        D    = (bf[:, 0] - spm.spm_hrf(dt, p, fMRI_T)) / dp
        D    = D[:, np.newaxis]
        bf   = np.append(bf, D, axis=1)
        p[5] = p[5] - dp
        # dispersion-derivative
        if xBF['TD_DD'] == 2:
            dp   = 0.01
            p[2] = p[2] + dp
            D    = (bf[:, 0] - spm.spm_hrf(dt, p, fMRI_T)) / dp
            D    = D[:, np.newaxis]
            bf   = np.append(bf, D, axis=1)
    return bf
