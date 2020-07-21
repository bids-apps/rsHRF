# Testing rsHRF-Python

The aim is to test the rsHRF-Toolbox (python version) against the stable-matlab version. For more details, click [here](https://github.com/BIDS-Apps/rsHRF/projects).

## VoxelTest
The functionality of both the toolboxes are compared against each other, for a single voxel (for a swift analysis).
```
VoxelTest
|   parameters.dat
|   rsHRF_matlab.m
|   rsHRF_python.py
|   compare.py
|   Data
└─>  └─> <Empty>
```

### parameters.dat

This file contains the parameters used for HRF estimation. Each parameter is specified as a numerical value on a separate line. The correspondence is as follows:

1. \<skipped>
2. **order**
3. **TR**
4. **passband-LHS**
5. **passband-RHS**
6. **T**
7. **T0**
8. **min_onset_search**
9. **max_onset_search**
10. **AR_lag**
11. **thr**
12. **len**
13. **voxel_id**

The *voxel_id* corresponds to the particular voxel under analysis. For more information about the other parameters, please refer to the documentation of the rsHRF-toolbox.

### rsHRF_matlab.m
This script executes the matlab-version of the rsHRF-toolbox.

Executing this script retrieves the HRF (with the parameters in the *parameters.dat* file), using all the basis-sets, and saves the retrieved time-series as a *.mat* file in the *Data* directory. The file name contains the information of the estimation-rule that was used to retrieve the HRF.

### rsHRF_python.py
This script executes the python-version of the rsHRF-toolbox.

Most of the details are similar to the *rsHRF_matlab.m*. The retrieved time-series gets stores in a *.txt* file in the *Data* directory.

### compare.py

Having run both the above scripts, *compare.py* compares the retrieved HRF corresponding to the python and matlab versions. It returns the Pearsons' Correlation between the time-series estimated through each estimation rule.

### Note
The fMRI data has not been provided in the repository. To download, visit this [link](https://www.nitrc.org/frs/?group_id=1304), and set the paths to input files accordingly.