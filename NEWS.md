# Unreleased

* `[Fixed]` `write_derivative_description` raised `KeyError` when `RSHRF_DOCKER_TAG` was set, and wrote
  `"URI": null` when `RSHRF_SINGULARITY_URL` was set. Both branches now read the variable they gate on.
* `[Fixed]` `write_derivative_description` no longer prints the version string to stdout.
* `[Fixed]` `spm_detrend` raised `TypeError` for polynomial order > 0.
* `[Fixed]` the `linalg.solve` fallbacks in `sFIR/smooth_fir.py` assigned `lstsq`'s 4-tuple
  rather than its solution, so they raised `ValueError` instead of falling back.
* `[Fixed]` the `--temporal-mask` parser now rejects files containing anything other than 0s, 1s and separators, instead of silently dropping the bad characters and building a wrong-length mask.

# rsHRF 1.5.8
## 12th September, 2021
* `[Fixed]` Fixed bugs for rest_filter (was only estimating the first 5000 voxels.)

# rsHRF 1.4.4
## 19th february, 2021
*  `[Changed]` Default `para['T0']` value to 1 instead of 3.
*  `[Changed]` Changed float to int value (for `--T0` argument).
*  `[Fixed]` Fixed bugs for default sFIR `para['T']` value.


# rsHRF 1.4.3
## 10th february, 2021
*  `[Fixed]` Fixed bugs in HRF plots.

# rsHRF 1.4.1
## 4th January, 2021
*  `[Fixed]` Fixed dependency bugs.

# rsHRF 1.4.0
## 20th December, 2020
*  `[Added]` Temporal filter.
*  `[Added]` Wiener deconvolution.
*  `[Fixed]` Fixed bugs in logging-window (GUI).
# rsHRF 1.3.9
## 15th November, 2020
* `[Fixed]` Fixed bugs with GUI.

# rsHRF 1.3.6 [WITHDRAWN]
## 28th October, 2020
* `[Changed]` Removed GUI from docker-version.

# rsHRF 1.3.1
## 23rd August, 2020
*  `[Added]` Application of passband filter for BOLD deconvolution (using `--passband_deconvolve` argument).

# rsHRF 1.3.0
## 13th August, 2020
* `[Added]` Graphical User Interface.

# rsHRF 1.2.2
## 10th August, 2020

* `[Added]` Standalone time-series input (.txt).
* `[Added]` Implicit generation of brain-mask.
* `[Fixed]` Minor bugs, raising appropriate errors, etc.

# rsHRF 1.1.1
## 24th July, 2020

* `[Added]` Fourier, Gamma and Hanning basis functions.
* `[Added]` .gii / .gii.gz input format.
* `[Changed]` Converted positional arguments to keyword arguments.
* `[Changed]` Made it mandatory to provide output-directory.
* `[Changed]` Algorithm for hemodynamic response function.
