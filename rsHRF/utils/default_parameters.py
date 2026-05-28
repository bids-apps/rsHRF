import numpy as np
import sys

default_parameters = {}

# Default estimation method: canonical HRF with time and dispersion derivatives.
default_parameters["estimation"] = "canon2dd"

# Temporal band-pass filter used for the BOLD signal.
default_parameters["passband"] = [0.01, 0.08]

# No additional band-pass filtering during deconvolution by default.
default_parameters["passband_deconvolve"] = [0.0, sys.float_info.max]

# TR is read from BIDS metadata when using BIDS input; non-BIDS users must provide it.
default_parameters["TR"] = -1

# Local peak width used for point-process event detection.
default_parameters["localK"] = 1

# Microtime resolution factor; dt = TR / T.
default_parameters["T"] = 3

# Reference microtime bin for onset estimation.
default_parameters["T0"] = 1

# Use canonical HRF with time and dispersion derivatives by default.
default_parameters["TD_DD"] = 2

# AR(1) serial correlation model.
default_parameters["AR_lag"] = 1

# Event detection threshold: mean + thr * standard deviation.
default_parameters["thr"] = 1

# Number of basis functions for gamma/fourier/hanning models.
default_parameters["order"] = 3

# Volterra expansion is disabled by default.
default_parameters["volterra"] = 0

# HRF duration in seconds.
default_parameters["len"] = 24

# Empty temporal mask: no events are excluded by default.
default_parameters["temporal_mask"] = []

# Minimum and maximum event-to-HRF onset delay in seconds.
default_parameters["min_onset_search"] = 4
default_parameters["max_onset_search"] = 8

default_parameters["wiener"] = False
default_parameters["dt"] = -1
default_parameters["lag"] = np.arange(
    0,
    0,
    dtype="int",
)

available_estimations = ["canon2dd", "sFIR", "FIR", "fourier", "hanning", "gamma"]
