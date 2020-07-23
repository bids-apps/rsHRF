# Changelog (For Users)

## Version 1.1.0 (July 22, 2020)

### Additions:

* Extended estimation-procedures to include gamma, fourier and fourier-with-hanning basis sets.
* Added GIfTI format compatibility for stand-alone analysis.

### Alterations:

* The *output_dir* needs to specified using *--output_dir* for all three execution modes (stand-alone analysis, BIDS with atlas, BIDS).
* In case of BIDS or BIDS with atlas, the *bids_dir* needs to be specified using *bids_dir*, and *analysis_level* needs to be specified using *analysis_level*.

**Example:**
1. Stand-alone mode
``` bash
    rsHRF --input_file sub-10171_task-rest_bold_space-T1w_preproc.nii --atlas sub-10171_task-rest_bold_space-T1w_brainmask.nii --estimation gamma --output_dir output_gamma
```
2. BIDS w/ atlas mode
``` bash
    rsHRF --bids_dir sub-10171 --atlas sub-10171/func/sub-10171_task-rest_bold_space-T1w_brainmask.nii --estimation gamma --analysis_level participant --output_dir output_gamma
```
3. BIDS mode
``` bash
    rsHRF --bids_dir sub-10171 --brainmask --estimation gamma --analysis_level participant --output_dir output_gamma
```