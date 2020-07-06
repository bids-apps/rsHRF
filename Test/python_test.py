import matplotlib
matplotlib.use('agg')
import numpy as np
import os
import time
import matplotlib.pyplot as plt
from scipy import stats, signal
from scipy.sparse import lil_matrix
import scipy.io as sio
import warnings
from rsHRF import spm_dep, processing, canon, sFIR, parameters, basis_functions, utils
import nibabel as nib
warnings.filterwarnings("ignore")

# Parameters for analysis
para = {}
BF = ['canon2dd', 'canon2dd', 'gamma', 'fourier', 'fourier w hanning']
Name = ['Canonical HRF (with time derivative)', 'Canonical HRF (with time and dispersion derivatives)',
    'Gamma functions', 'Fourier set', 'Fourier set (Hanning)']

parameterFile = np.loadtxt("./Data/Input/parameters.dat")

para['estimation'] = BF[int(parameterFile[0]-1)]
TD_DD = parameterFile[0]
para['order'] = int(parameterFile[1])
para['TR'] = parameterFile[2]
para['passband'] = [parameterFile[3], parameterFile[4]]
para['T'] = int(parameterFile[5])
para['T0'] = int(parameterFile[6])
para['min_onset_search'] = int(parameterFile[7])
para['max_onset_search'] = int(parameterFile[8])
para['AR_lag'] = int(parameterFile[9])
para['thr'] = int(parameterFile[10])
para['len'] = int(parameterFile[11])
para['dt'] = para['TR']/para['T']
para['lag'] = np.arange(np.fix(para['min_onset_search'] / para['dt']),
                    np.fix(para['max_onset_search'] / para['dt']) + 1,
                    dtype='int')


# Testing for the case where we have input and atlas as separate files
input_file = "/home/redhood/Desktop/Work/GSoC/rsHRF-Toolbox/rsHRF-GUI/Input/sub-031274_task-rest_bold.nii"
mask_file = "/home/redhood/Desktop/Work/GSoC/rsHRF-Toolbox/rsHRF-GUI/Input/sub-031274_task-rest_bold_brain.nii"
file_type = ".nii"
mode = "file"

name = input_file.split('/')[-1].split('.')[0]
v = spm_dep.spm.spm_vol(mask_file)
v1 = spm_dep.spm.spm_vol(input_file)
brain = spm_dep.spm.spm_read_vols(v)
voxel_ind = np.where(brain > 0)[0]
data = v1.get_data()
nobs = data.shape[3]
data1 = np.reshape(data, (-1, nobs), order='F').T
bold_sig = stats.zscore(data1[:, voxel_ind], ddof=1)
mask = v.get_data()
bold_sig = np.nan_to_num(bold_sig)
bold_sig = processing. \
    rest_filter. \
    rest_IdealFilter(bold_sig, para['TR'], para['passband'])

data_deconv = np.zeros(bold_sig.shape)
event_number = np.zeros((1, bold_sig.shape[1]))

start_time = time.time()
beta_hrf, event_bold, bf = utils.hrf_estimation.compute_hrf(bold_sig, para, [], 1)
hrfa = np.dot(bf, beta_hrf[np.arange(0, bf.shape[1]), :])
print("--- %s seconds ---" % (time.time() - start_time))

np.savetxt("./Data/hrf" + Name[int(parameterFile[0]-1)] +"_kenzo.txt", hrfa,delimiter=", ")