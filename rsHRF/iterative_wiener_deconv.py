import pywt
import numpy as np
from scipy.signal.windows import gaussian
from scipy.signal import convolve
from rsHRF.processing import knee
import warnings


def rsHRF_iterative_wiener_deconv(y, h,
                                   TR=None,
                                   MaxIter=None,
                                   Tol=1e-4,
                                   Mode='rest',
                                   Smooth=None,
                                   LowPass=None,
                                   Iterations=None):
    """
    Iterative Wiener-like deconvolution with wavelet-based noise estimation.

    Updated to match MATLAB v2.5 (September 2025) with:
    - Dynamic noise estimation
    - Signal preprocessing (mean-centering)
    - Gaussian smoothing
    - Low-pass filtering
    - Auto-recommendations for rest/task modes
    - Convergence detection

    Parameters
    ----------
    y : ndarray
        Observed signal (N x 1)
    h : ndarray
        HRF or system impulse response (Nh x 1)
    TR : float, optional
        Sampling interval in seconds. Required for auto-recommendations.
    MaxIter : int, optional
        Maximum number of iterations (default: 50)
    Tol : float, optional
        Convergence tolerance (default: 1e-4)
    Mode : str, optional
        Acquisition mode: 'rest' or 'task' (default: 'rest')
        Used for auto-recommendations of Smooth and LowPass parameters.
    Smooth : int, optional
        Temporal smoothing window size in points.
        If None, auto-recommended based on Mode and TR.
    LowPass : float, optional
        Low-pass cutoff frequency in Hz.
        If None, auto-recommended based on Mode and TR.
    Iterations : int, optional
        DEPRECATED: Use MaxIter instead. Kept for backward compatibility.

    Returns
    -------
    xhat : ndarray
        Deconvolved signal

    Notes
    -----
    This implementation follows the MATLAB v2.5 update by Guorong Wu (2025-09)
    which addressed sinusoidal artifacts and edge effects in the deconvolution.

    References
    ----------
    Wu, G.R., et al. (2021). rsHRF: A Toolbox for Resting-State HRF
    Estimation and Deconvolution. NeuroImage, 244, 118591.

    Examples
    --------
    >>> # Rest fMRI with auto-recommendations
    >>> data_deconv = rsHRF_iterative_wiener_deconv(bold_signal, hrf,
    ...                                              TR=0.72, Mode='rest')

    >>> # Task fMRI with custom parameters
    >>> data_deconv = rsHRF_iterative_wiener_deconv(bold_signal, hrf,
    ...                                              TR=2.0, Mode='task',
    ...                                              Smooth=5, LowPass=0.4)
    """

    # ============ PARAMETER PARSING ============

    # Backward compatibility: handle deprecated Iterations parameter
    if Iterations is not None and MaxIter is None:
        warnings.warn(
            "Parameter 'Iterations' is deprecated. Use 'MaxIter' instead. "
            "Iterations will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2
        )
        MaxIter = Iterations

    # Set default MaxIter if not provided
    if MaxIter is None:
        MaxIter = 50

    # ============ PREPROCESSING ============

    # Mean-center to remove DC offset (MATLAB v2.5 line 28)
    y_mean = np.nanmean(y)
    y = y - y_mean

    # Ensure y and h are 1D arrays
    y = y.flatten()
    h = h.flatten()

    N = y.shape[0]
    nh = h.shape[0]

    # Pad HRF to signal length
    if nh < N:
        h = np.pad(h, (0, N - nh), mode='constant', constant_values=0)
    elif nh > N:
        h = h[:N]

    # Calculate sampling rate
    if TR is not None:
        fs = 1.0 / TR
        nyquist = fs / 2.0
    else:
        fs = 1.0
        nyquist = 0.5

    # ============ AUTO-RECOMMENDATIONS ============
    # Based on MATLAB v2.5 lines 44-58

    if Smooth is None or LowPass is None:
        if Mode.lower() == 'rest':
            if TR is not None:
                smooth_rec = max(int(np.round(4.0 / TR)), 3)
                lowpass_rec = min(0.2, 0.8 * nyquist)
            else:
                smooth_rec = 3
                lowpass_rec = 0.2
        elif Mode.lower() == 'task':
            if TR is not None:
                smooth_rec = max(int(np.round(2.0 / TR)), 2)
                lowpass_rec = min(0.35, 0.9 * nyquist)
            else:
                smooth_rec = 2
                lowpass_rec = 0.35
        else:
            raise ValueError(f"Unknown Mode: {Mode}. Use 'rest' or 'task'.")

    # Apply auto-recommendations if parameters not provided
    if Smooth is None:
        Smooth = smooth_rec
    if LowPass is None:
        LowPass = lowpass_rec

    # ============ FFT PREPROCESSING ============

    H = np.fft.fft(h, axis=0)
    Y = np.fft.fft(y, axis=0)

    # Initial estimate
    xhat = y.copy()
    Pxx = np.abs(Y)**2

    # ============ INITIAL NOISE ESTIMATION ============
    # Wavelet-based noise estimation using MAD method

    coeffs = pywt.wavedec(np.abs(y), 'db2', level=1)
    detail_coeffs = coeffs[-1]
    sigma = np.median(np.abs(detail_coeffs)) / 0.6745
    Nf = sigma**2 * N

    # ============ ITERATIVE PROCESS ============

    for iteration in range(MaxIter):
        # Wiener-like update (MATLAB v2.5 lines 76-81)
        M = (np.conj(H) * Pxx * Y) / (np.abs(H)**2 * Pxx + Nf)
        PxxY = (Pxx * Nf) / (np.abs(H)**2 * Pxx + Nf)
        Pxx_new = PxxY + np.abs(M)**2

        WienerFilterEst = (np.conj(H) * Pxx_new) / (np.abs(H)**2 * Pxx_new + Nf)
        xhat_new = np.real(np.fft.ifft(WienerFilterEst * Y))

        # ============ GAUSSIAN SMOOTHING ============
        # MATLAB v2.5 lines 84-88

        if Smooth > 1:
            # Create Gaussian window
            g = gaussian(int(Smooth), std=Smooth/4.0)
            g = g / np.sum(g)  # Normalize
            # Convolve with 'same' mode to maintain signal length
            xhat_new = convolve(xhat_new, g, mode='same')

        # ============ LOW-PASS FILTERING ============
        # MATLAB v2.5 lines 90-96

        if LowPass < nyquist:
            f = np.arange(N) / N * fs
            Xf = np.fft.fft(xhat_new)
            Xf[f > LowPass] = 0
            xhat_new = np.real(np.fft.ifft(Xf))

        # ============ DYNAMIC NOISE UPDATE ============
        # MATLAB v2.5 lines 98-102

        # Compute residual
        residual = y - convolve(xhat_new, h, mode='same')

        # Re-estimate noise from residual
        coeffs = pywt.wavedec(np.abs(residual), 'db2', level=1)
        detail_coeffs = coeffs[-1]
        sigma = np.median(np.abs(detail_coeffs)) / 0.6745
        Nf = sigma**2 * N

        # ============ CONVERGENCE CHECK ============
        # MATLAB v2.5 lines 105-108

        norm_diff = np.linalg.norm(xhat_new - xhat)
        norm_xhat = np.linalg.norm(xhat)

        if norm_xhat > 0 and (norm_diff / norm_xhat) < Tol:
            xhat = xhat_new
            break

        # Update for next iteration
        xhat = xhat_new
        Pxx = Pxx_new

    return xhat
