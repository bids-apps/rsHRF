import pyyawt
import numpy as np 
from   rsHRF.processing import knee 

def rsHRF_iterative_wiener_deconv(y, h, Iterations=1000):
    N            = y.shape[0]
    nh           = max(h.shape)
    h            = np.append(h, np.zeros((N - nh, 1)))
    H            = np.fft.fft(h, axis=0)
    Y            = np.fft.fft(y, axis=0)
    [c ,l]       = pyyawt.wavedec(abs(y), 1, 'db2')
    sigma        = pyyawt.wnoisest(c, l, 1)
    Phh          = np.square(abs(H))
    sqrdtempnorm = ((((np.linalg.norm(y-np.mean(y), 2)**2) - (N-1)*(sigma**2)))/(np.linalg.norm(h,1))**2)
    Nf           = (sigma**2)*N
    tempreg      = Nf/sqrdtempnorm
    Pxx0         = np.square(abs(np.multiply(Y, (np.divide(np.conj(H), (Phh + N*tempreg))))))
    Pxx          = Pxx0
    Sf           = Pxx.reshape(-1, 1)
    for i in range(0, Iterations):
        M           = np.divide(np.multiply(np.multiply(np.conjugate(H), Pxx), Y), np.add(np.multiply(np.square(abs(H)), Pxx), Nf))
        PxxY        = np.divide(np.multiply(Pxx, Nf), np.add(np.multiply(np.square(abs(H)), Pxx), Nf))
        Pxx         = np.add(PxxY, np.square(abs(M)))
        Sf          = np.concatenate((Sf, Pxx.reshape(-1, 1)), axis = 1)
    dSf             = np.diff(Sf, 1, 1)
    dSfmse          = np.mean(np.square(dSf), axis=1)
    _, idx          = knee.knee_pt(dSfmse)
    idm             = np.argmin(dSfmse)
    ratio           = np.abs(dSfmse[idx] - dSfmse[idm])/(np.abs(np.max(dSfmse) - np.min(dSfmse)))
    if ratio > 0.5:
        id0 = idm 
    else:
        id0 = idx 
    Pxx             = Sf[:,id0+1]
    WienerFilterEst = np.divide(np.multiply(np.conj(H), Pxx), np.add(np.multiply(np.square(abs(H)), Pxx), Nf))
    return np.real(np.fft.ifft(np.multiply(WienerFilterEst, Y)))