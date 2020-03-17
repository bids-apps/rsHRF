import numpy as np
from scipy.sparse import lil_matrix
from scipy import stats, linalg
from joblib import Parallel, delayed
from joblib import load, dump
import tempfile
import shutil
import os
import warnings
from ..spm_dep import spm
from ..processing import knee
from rsHRF import basis_functions

warnings.filterwarnings("ignore")


def tor_make_deconv_mtx3(sf, tp, eres):
    docenter = 0
    if type(sf) is not dict:
        sf2 = {}
        for i in range(0, sf.shape[1]):
            sf2[i] = sf[:, i]
        sf = sf2
    if type(tp) is int:
        tp = np.tile(tp, (1, len(sf)))
    if len(tp) != len(sf):
        print('timepoints vectors (tp) and \
        stick function (sf) lengths do not match!')
        return
    tbefore = 0
    nsess = len(sf)

    numtrs = int(np.around(np.amax(sf[0].shape) / eres))
    myzeros = np.zeros((numtrs, 1))
    DX = np.zeros((numtrs, 1))

    for i in range(0, len(sf)):
        Snumtrs = np.amax(sf[i].shape) / eres
        if(Snumtrs != np.round(Snumtrs)):
            print('length not evenly divisible by eres')
        if(numtrs != Snumtrs):
            print('different length than sf[0]')

        inums = np.nonzero(sf[i] > 0)[0]
        inums = inums / eres
        inums = np.ceil(inums).astype(int)
        sf[i] = np.ravel(myzeros)
        sf[i][inums] = 1

    index = 0
    for i in range(0, len(sf)):
        if tbefore != 0:
            for j in range(tbefore - 1, -1, -1):
                sf_temp = sf[i][j:]
                sf_temp = sf_temp[:, np.newaxis]
                mysf = np.concatenate((sf_temp, np.zeros((j, 1))))
                if index == 0:
                    DX[:, index] = np.ravel(mysf)
                else:
                    DX = np.column_stack((DX, mysf))
                index += 1

        if index == 0:
            DX[:, index] = sf[i]
        else:
            DX = np.column_stack((DX, sf[i]))

        index += 1
        inums = np.nonzero(sf[i] == 1)[0]

        for j in range(1, np.ravel(tp)[i]):
            myzeros = np.zeros((numtrs, 1))
            inums = inums + 1
            reg = myzeros
            inums = inums[inums < numtrs]
            reg[inums] = 1
            while (np.amax(reg.shape) < DX.shape[0]):
                reg = np.concatenate((reg, np.zeros(1, 1)))
            DX = np.column_stack((DX, reg))
            index += 1

    if nsess < 2:
        DX = np.column_stack((DX, np.ones((DX.shape[0], 1))))
    else:
        X = np.zeros((DX.shape[0], 1))
        index = 0
        scanlen = DX.shape[0] / nsess
        if np.around(scanlen) != scanlen:
            print('Model length is not an even multiple of scan length.')
        for startimg in range(0, DX.shape[0], int(np.around(scanlen))):
            if index == 0:
                X[startimg:startimg + int(np.around(scanlen)), index] = 1
            else:
                X_temp = np.zeros((DX.shape[0], 1))
                X_temp[startimg:startimg + int(np.around(scanlen)), 0] = 1
                X = np.column_stack((X, X_temp))
            index += 1
        DX = np.column_stack((DX, X))

    if docenter:
        wh = np.arange(1, DX.shape[1] - nsess + 1)
        DX[:, wh] = DX[:, wh] - np.tile(np.mean(DX[:, wh]), (DX.shape[0], 1))
    return DX, sf


def Fit_sFIR2(tc, TR, Runs, T, mode, ARlag):
    DX, sf = tor_make_deconv_mtx3(Runs, T, 1)
    DX2 = DX[:, 0:T]
    num = T

    if mode == 1:
        C = np.arange(1, num + 1).reshape((1, num)).conj().T\
            .dot(np.ones((1, num)))
        h = np.sqrt(1 / (7 / TR))

        v = 0.1
        sig = 1

        R = v * np.exp(-h / 2 * (C - C.conj().T) ** 2)
        RI = np.linalg.inv(R)

        sMRI = sig**2*RI
        #sMRI = np.zeros((num+1,num+1))
        #sMRI[:-1,:-1] = sMRI0

        if ARlag == 1:
            b = np.linalg.solve((DX2.conj().T.dot(DX2) + sig ** 2 * RI),
                                DX2.conj().T).dot(tc)
            e = tc - DX2.dot(b)
        else:
            e, b = wgr_glsco(DX2,tc,sMRI,AR_lag=ARlag)

    elif mode == 0:
        b = np.linalg.pinv(DX).dot(tc)
        if ARlag == 1:
            e = tc - DX.dot(b)
            b = b[0:T]
        else:
            e, b = wgr_glsco(DX2,tc,[],AR_lag=ARlag)

    hrf = b

    return hrf, e

def wgr_FIR_estimation_HRF(u, dat, para, N):
    if para['estimation'] == 'sFIR':
        firmode = 1
    else:
        firmode = 0

    lag = para['lag']
    nlag = np.amax(lag.shape)
    len_bin = int(np.floor(para['len'] / para['TR']))

    hrf = np.zeros((len_bin, nlag))

    Cov_E = np.zeros((1, nlag))
    kk = 0

    for i_lag in range(1, nlag + 1):
        RR = u - i_lag
        RR = RR[RR >= 0]
        if RR.size != 0:
            design = np.zeros((N, 1))
            design[RR] = 1
            hrf_kk, e3 = Fit_sFIR2(dat, para['TR'], design, len_bin, firmode,para['AR_lag'])
            hrf[:, kk] = np.ravel(hrf_kk)
            Cov_E[:, kk] = np.cov(np.ravel(e3))
        else:
            Cov_E[:, kk] = np.inf
        kk += 1

    placeholder, ind = knee.knee_pt(np.ravel(Cov_E))
    rsH = hrf[:, ind + 1]
    return rsH, u

def wgr_glsco(X, Y, sMRI, AR_lag=1, max_iter=20):
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
        Beta = np.linalg.lstsq(X, Y, rcond=None)[0]
    else:
        Beta = np.linalg.lstsq((np.matmul(X.T,X) + sMRI),np.matmul(X.T,Y))[0]

    resid = Y - (X.dot(Beta))

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
        AR_para = np.linalg.lstsq(X_AR, Y_AR, rcond=None)[0]

        X_main = X[AR_lag:nobs, :]
        Y_main = Y[AR_lag:nobs]

        for m in range(AR_lag):
            X_main = \
                X_main - (AR_para[m] * (X[AR_lag - m - 1:nobs - m - 1, :]))
            Y_main = Y_main - (AR_para[m] * (Y[AR_lag - m - 1:nobs - m - 1]))

        if sMRI == []:
            Beta = np.linalg.lstsq(X_main, Y_main, rcond=None)[0]
        else:
            Beta = np.linalg.lstsq((np.matmul(X_main.T,X_main) + sMRI),np.matmul(X_main.T,Y_main))[0]

        resid = Y[AR_lag:nobs] - X[AR_lag:nobs, :].dot(Beta)
        if(max(np.absolute(Beta - Beta_temp)) < max_tol):
            break
    res_sum = np.cov(resid)
    return res_sum, Beta
