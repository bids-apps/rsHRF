import numpy as np
import numpy.matlib
import warnings

warnings.filterwarnings("ignore")

def rest_IdealFilter(x, TR, Bands, m=5000):
    nvar = x.shape[1]
    nbin = int(np.ceil(nvar/m))
    for i in range(1, nbin + 1):
        if i != nbin:
            ind_X = [j for j in range((i-1)*m, i*m)]
        else:
            ind_X = [j for j in range((i-1)*m, nvar)]
        x1 = x[:, ind_X]
        x1 = conn_filter(TR,Bands,x1) + np.matlib.repmat(np.mean(x1), x1.shape[0], 1)
        x[:,ind_X] = x1
    return x
        
def conn_filter(rt, filter, x):
    Nx = x.shape[0]
    fy = np.fft.fft(np.concatenate((x, np.flipud(x)), axis=0), axis=0)
    f = np.arange(fy.shape[0])
    f = f.reshape(1, -1)
    f = np.min((f, fy.shape[0]-f), axis=0)
    low = filter[0]*(rt*fy.shape[0])
    high = filter[1]*(rt*fy.shape[0])
    idx_low = np.argwhere(np.any(f < low, axis=0))
    idx_high = np.argwhere(np.any(f >= high, axis=0))
    idx = np.concatenate((idx_low, idx_high)).reshape(-1)
    fy[idx,:] = 0.
    y = np.real(np.fft.ifft(fy, axis=0))
    y = y[0:Nx,:]
    return y