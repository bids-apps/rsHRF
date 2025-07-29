import numpy as np
from scipy        import linalg
from ..processing import knee

import warnings
warnings.filterwarnings("ignore")

def wgr_regress(y, X):
    n, ncolX = X.shape
    Q,R,perm = linalg.qr(X, mode='economic', pivoting=True)
    if R.ndim == 0:
        p = 0
    elif R.ndim == 1:
        p = int(abs(R[0]) > 0)
    else:
        if np.amin(R.shape) == 1:
            p = int(abs(R[0]) > 0)
        else:
            p = np.sum(np.abs(np.diagonal(R)) > abs(max(n, ncolX)*np.spacing(R[0][0])))
    if p < ncolX:
        R = R[0:p,0:p]
        Q = Q[:,0:p]
        perm = perm[0:p]
    b = np.zeros((ncolX))
    if(R.shape[0] == R.shape[1]):
        try:
            b[perm] = linalg.solve(R,np.matmul(Q.T,y))
        except:
            b[perm] = linalg.lstsq(R,np.matmul(Q.T,y))
    else:
        b[perm] = linalg.lstsq(R,np.matmul(Q.T,y))
    return b

def wgr_glsco(X, Y, sMRI = [], AR_lag=0, max_iter=20):
    """
    Linear regression when disturbance terms follow AR(p)
    -----------------------------------
    Model:
    Yt = Xt * Beta + ut ,
    ut = Phi1 * u(t-1) + ... + Phip * u(t-p) + et
    where et ~ N(0,s^2)
    -----------------------------------
    Algorithm:
    Cochrane-Orcutt iterated regression (Feasible generalized least squares)
    -----------------------------------
    Usage:
    Y = dependent variable (n * 1 vector)
    X = regressors (n * k matrix)
    AR_lag = number of lags in AR process
    -----------------------------------
    Returns:
    Beta = estimator corresponding to the k regressors
    """
    nobs, nvar = X.shape
    if sMRI == []:
        Beta = wgr_regress(Y,X)
    else:
        sMRI = np.array(sMRI)
        try:
            Beta = linalg.solve(np.matmul(X.T,X)+sMRI,np.matmul(X.T,Y))
        except:
            Beta = linalg.lstsq(np.matmul(X.T,X)+sMRI,np.matmul(X.T,Y))
    resid = Y - np.matmul(X,Beta)
    if AR_lag == 0:
        res_sum = np.cov(resid)
        return res_sum, Beta
    max_tol = min(1e-6, max(np.absolute(Beta)) / 1000)
    for r in range(max_iter):
        Beta_temp = Beta
        X_AR = np.zeros((nobs - (2 * AR_lag), AR_lag))
        for m in range(AR_lag):
            X_AR[:, m] = resid[AR_lag - m - 1:nobs - AR_lag - m - 1]
        Y_AR = resid[AR_lag:nobs - AR_lag]
        AR_para = wgr_regress(Y_AR, X_AR)
        X_main = X[AR_lag:nobs, :]
        Y_main = Y[AR_lag:nobs]
        for m in range(AR_lag):
            X_main = \
                X_main - (AR_para[m] * (X[AR_lag - m - 1:nobs - m - 1, :]))
            Y_main = Y_main - (AR_para[m] * (Y[AR_lag - m - 1:nobs - m - 1]))
        if sMRI == []:
            Beta = wgr_regress(Y_main, X_main)
        else:
            try:
                Beta = linalg.solve(np.matmul(X_main.T,X_main)+sMRI,np.matmul(X_main.T,Y_main))
            except:
                Beta = linalg.lstsq(np.matmul(X_main.T,X_main)+sMRI,np.matmul(X_main.T,Y_main))
        resid = Y[AR_lag:nobs] - X[AR_lag:nobs, :].dot(Beta)
        if(max(np.absolute(Beta - Beta_temp)) < max_tol):
            break
    res_sum = np.cov(resid)
    return res_sum, Beta
    
def Fit_sFIR2(output, length, TR, input, T, flag_sfir, AR_lag):
    NN = int(np.floor(length/TR))
    _input = np.expand_dims(input[0], axis=0)
    X = linalg.toeplitz(input, np.concatenate((_input, np.zeros((1, NN-1))), axis = 1))
    X = np.concatenate((X, np.ones((input.shape))), axis = 1)
    if flag_sfir:
        fwhm = 7 #fwhm=7 seconds smoothing - ref. Goutte
        nh = NN-1
        dt = TR
        _ = np.expand_dims(np.arange(1, nh+1).T, axis=1)
        C = np.matmul(_,np.ones((1, nh)))
        h = np.sqrt(1./(fwhm/dt))
        v = 0.1
        R = v * np.exp(-h/2 * (C-C.T)**2)
        RI = linalg.inv(R)
        MRI = np.zeros((nh + 1, nh + 1))
        MRI[0:nh,0:nh] = RI;
        sigma = 1
        sMRI0 = sigma**2*MRI
        sMRI = np.zeros((NN+1, NN+1))
        sMRI[0:NN,0:NN] = sMRI0; 
        if AR_lag == 0:
            try:
                hrf = linalg.solve((np.matmul(X.T,X)+sMRI),np.matmul(X.T,output))
            except:
                hrf = linalg.lstsq((np.matmul(X.T,X)+sMRI),np.matmul(X.T,output))
            resid = output - np.matmul(X, hrf)
            res_sum = np.cov(resid)
        else:
            res_sum, hrf = wgr_glsco(X,output,AR_lag=AR_lag,sMRI=sMRI);
    else:
        if AR_lag == 0:
            hrf = linalg.lstsq(X,output)
            hrf = hrf[0]
            resid = output - np.matmul(X, hrf)
            res_sum = np.cov(resid)
        else:
            res_sum, hrf = wgr_glsco(X,output,AR_lag=AR_lag)
    return hrf, res_sum

def wgr_FIR_estimation_HRF(u, dat, para, N):
    if para['estimation'] == 'sFIR':
        firmode = 1
    else:
        firmode = 0
    lag = para['lag']
    nlag = np.amax(lag.shape)
    len_bin = int(np.floor(para['len'] / para['TR']))
    hrf = np.zeros((len_bin+1, nlag))
    Cov_E = np.zeros((1, nlag))
    kk = 0
    for i_lag in range(1, nlag + 1):
        RR = u - i_lag
        RR = RR[RR >= 0]
        if RR.size != 0:
            design = np.zeros((N, 1))
            design[RR] = 1
            hrf_kk, e3 = Fit_sFIR2(dat, para['len'], para['TR'], design, len_bin, firmode, para['AR_lag'])
            hrf[:, kk] = np.ravel(hrf_kk)
            Cov_E[:, kk] = (np.ravel(e3))
        else:
            Cov_E[:, kk] = np.inf
        kk += 1
    placeholder, ind = knee.knee_pt(np.ravel(Cov_E))
    if ind == np.amax(Cov_E.shape) - 1:
        ind = ind - 1
    rsH = hrf[:,ind+1]
    return rsH, u