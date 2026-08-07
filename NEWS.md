# Unreleased

* `[Fixed]` `write_derivative_description` raised `KeyError` when `RSHRF_DOCKER_TAG` was set, and wrote
  `"URI": null` when `RSHRF_SINGULARITY_URL` was set. Both branches now read the variable they gate on.
* `[Fixed]` `write_derivative_description` no longer prints the version string to stdout.
* `[Fixed]` `spm_detrend` raised `TypeError` for polynomial order > 0.
* `[Fixed]` the `linalg.solve` fallbacks in `sFIR/smooth_fir.py` assigned `lstsq`'s 4-tuple
  rather than its solution, so they raised `ValueError` instead of falling back.
* `[Fixed]` the `--temporal-mask` parser now rejects files containing anything other than 0s, 1s and separators, instead of silently dropping the bad characters and building a wrong-length mask.
* `[Changed]` removed the unused `mpld3` import and the unused `duecredit` dependency.
* `[Fixed]` the repository URL in `__about__.py` (`BIDSapps` -> `BIDS-Apps`).
* `[Fixed]` file paths are now parsed with `os.path.basename` instead of `split("/")`, so filename and subject-ID extraction works on Windows.
* `[Fixed]` the "No Events Detected!" check now looks at the events of the voxel being plotted (`event_bold[pos]`) instead of the size of the whole `event_bold` array, which was almost always non-zero. Also guards against `pos` overflowing when no voxel has an HRF.
* `[Fixed]` the BIDS processing loop now catches `Exception` instead of a bare `except:`, so `KeyboardInterrupt` (Ctrl+C) and `SystemExit` are no longer swallowed while iterating over input-mask pairs.
* `[Fixed]` the GIfTI mask/input dimension check compared the input to itself (`v` vs `v`) so it never detected a mismatch; it now compares the input against the mask (`v1` vs `v`), like the NIfTI branch.
* `[Fixed]` `test_gnii` now derives `localK` from `TR` the same way `CLI.py` does, so the test matches the runtime behaviour introduced in #37 instead of comparing against the raw `None` default.
* `[Changed]` Replaced deprecated `numpy.matlib.repmat` with `numpy.tile` in `rest_filter.py`; `numpy.matlib` is deprecated and the two produce identical output for the scalar-mean broadcast used here.
* `[Fixed]` FIR/sFIR estimation now recomputes the lag range after `T` is reset to 1, and the search loop iterates over the lag values instead of the loop counter, so it searches delays within the requested `[min_onset_search, max_onset_search]` window instead of drifting outside it.
* `[Fixed]` `wgr_get_parameters` read the response height one sample too early when the peak sits at the end of a plateau: the plateau walk-back assigned `hdrf[cnt - 1]` where MATLAB's `rsHRF_get_HRF_parameters.m` uses `hdrf(cnt)`, i.e. `hdrf[cnt]` zero-based. Only the height map was affected; time-to-peak and FWHM were already correct.
* `[Fixed]` The GUI's FIR/sFIR path never reset `T` to 1 or recomputed the lag range, because `Core.retrieveHRF` calls `compute_hrf` directly instead of going through `fourD_rsHRF`. With the default `T = 3` it searched delays three times outside the requested window — 12-24s for the default `[4, 8]` request. Both paths now call `apply_fir_microtime_grid`, so the fix from #45 can no longer apply to one caller and not the other.
* `[Fixed]` `knee_pt` passed `knee_pt_helper`'s nan sentinel straight into an index expression, so bad input (an empty array, a 2D array, or anything that is not an ndarray) printed the helper's own diagnostic and then raised `ValueError`, `IndexError` or `TypeError` depending on the case — the useful message was buried under a NumPy internal one. The sentinel is now returned to the caller unchanged, which is what MATLAB's `knee_pt` does by raising `error()` at the same point.
* `[Fixed]` The `localK` derivation was duplicated in two places in `CLI.py` and missing entirely from the GUI, where `default_parameters["localK"]` is `None` and `Parameters` passes it straight through — so a GUI FIR/sFIR run raised `TypeError` on `1 + None` inside `wgr_BOLD_event_vector`. Both CLI sites and `Core.retrieveHRF` now call `utils.hrf_estimation.apply_localK_default`, which derives it from `TR` and leaves a user-supplied value untouched.
* `[Fixed]` `wgr_BOLD_event_vector` converted the 0/1 temporal mask into indices in place, leaving `0` at every dropped position, so each scrubbed frame entered the mean and standard deviation as `matrix[0]` instead of being excluded, and the resulting scale error changed which frames were detected as events. The conversion also wrote through to the caller's list, which `compute_hrf` shares across every voxel. Both are gone: the mask is now read with boolean indexing, the direct equivalent of MATLAB's `matrix(temporal_mask)`. Only runs that pass `--temporal-mask` are affected, and for those the detected events change.
* `[Fixed]` `estimate_hrf` assumed `para["thr"]` was a scalar, but the GUI's `set_thr` wraps it in a list for FIR/sFIR even when the user types a single number, so `np.array([para["thr"], np.inf])` built a ragged array and raised `ValueError`. Because `main.py` pushes the whole parameter form back through `set_parameters` on every update, this hit any GUI FIR/sFIR run once the user applied parameters, not just comma-separated input. Both branches now use `np.atleast_1d`, which accepts the scalar from the CLI and the list from the GUI; the CLI path is unchanged.
* `[Fixed]` The Wiener deconvolution read `deconv_MaxIter`, `deconv_Tol` and `deconv_mode` from `para`, but nothing ever set them and there were no CLI arguments, so `.get` always fell back to its hardcoded default and the parameters were unreachable. They are now exposed as `--deconv-maxiter`, `--deconv-tol` and `--deconv-mode`, with the defaults moved into `default_parameters`. Behaviour is unchanged at the defaults. Note that MATLAB's `rsHRF_deconv_job` passes `MaxIter = 10` while Python's default is 50.

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
