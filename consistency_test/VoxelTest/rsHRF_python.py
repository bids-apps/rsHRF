import os
import time
import numpy   as np
import nibabel as nib
from scipy import stats
from rsHRF import spm_dep, processing, utils, basis_functions

import warnings
warnings.filterwarnings("ignore")

# Create outputfolder
output_folder = os.getcwd() + '/Data'
if not os.path.isdir(output_folder):
    os.mkdir(output_folder)

# all the different estimation rules
BF =   ['canon2dd', 'canon2dd', 'gamma', 'fourier', 'fourier w hanning', 'FIR', 'sFIR']
Name = ['Canonical HRF (with time derivative)', 'Canonical HRF (with time and dispersion derivatives)', \
        'Gamma functions', 'Fourier set', 'Fourier set (Hanning)', \
        'FIR', 'sFIR']


parameterFile            = np.loadtxt("./parameters.dat") #loading the parameters from file
para                     = {}
para['order']            = int(parameterFile[1])
para['TR']               = parameterFile[2]
para['passband']         = [parameterFile[3], parameterFile[4]]
para['T']                = int(parameterFile[5])
para['T0']               = int(parameterFile[6])
para['min_onset_search'] = int(parameterFile[7])
para['max_onset_search'] = int(parameterFile[8])
para['AR_lag']           = int(parameterFile[9])
para['len']              = int(parameterFile[11])
para['dt']               = para['TR']/para['T']
para['lag']              = np.arange(np.fix(para['min_onset_search'] / para['dt']),
                        np.fix(para['max_onset_search'] / para['dt']) + 1,
                        dtype='int')
if para['TR']<=2:
    para['localK'] = 1
else:
    para['localK'] = 2
if para['T']  == 1:
    para['T0'] = 1

voxel_id = int(parameterFile[12]) 

# looping over all the estimation rules
for i in range(0, 7):
    para['estimation'] = BF[i]
    # for canonical estimation rule
    if i < 3:
        TD_DD = i%2 + 1
        para['TD_DD'] = int(TD_DD)
    if i < 7:
        para['thr']   = int(parameterFile[10])
    else:
        para['thr']   = [int(parameterFile[10])]
    path = '/home/redhood/Desktop/Work/GSoC-2020/rsHRF/Test/NITRC-multi-file-downloads/sub-10171/func/' # path to input directory
    input_file = path + 'sub-10171_task-rest_bold_space-T1w_preproc.nii'
    mask_file  = path + 'sub-10171_task-rest_bold_space-T1w_brainmask.nii'
    file_type  = ".nii"
    mode       = "file"
    name       = input_file.split('/')[-1].split('.')[0]

    v          = spm_dep.spm.spm_vol(mask_file)
    v1         = spm_dep.spm.spm_vol(input_file)
    brain      = spm_dep.spm.spm_read_vols(v)
    voxel_ind  = np.where(brain > 0)[0]
    data       = v1.get_data()
    nobs       = data.shape[3]
    data1      = np.reshape(data, (-1, nobs), order='F').T
    data1      = data1[:, voxel_ind]
    data1      = data1[:, voxel_id]
    bold_sig   = np.expand_dims(data1, axis=1)
    bold_sig   = stats.zscore(bold_sig, ddof=1)
    bold_sig   = processing. \
        rest_filter. \
        rest_IdealFilter(bold_sig, para['TR'], para['passband'])
    start_time = time.time()
    if not (para['estimation'] == 'sFIR' or para['estimation'] == 'FIR'):
        bf = basis_functions.basis_functions.get_basis_function(bold_sig.shape, para)
        beta_hrf, event_bold = utils.hrf_estimation.compute_hrf(bold_sig, para, [], 1, bf=bf)
        hrfa = np.dot(bf, beta_hrf[np.arange(0, bf.shape[1]), :])
    #Estimate HRF for FIR and sFIR
    else:
        beta_hrf, event_bold = utils.hrf_estimation.compute_hrf(bold_sig, para, [], 1)
        hrfa = beta_hrf[:-1,:]
    print("--- %s seconds ---" % (time.time() - start_time))
    print("Done")
    np.savetxt("./Data/hrf_" + Name[i] +"_python.txt", hrfa,delimiter=", ")
    i += 1