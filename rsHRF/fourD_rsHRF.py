import os
import matplotlib
matplotlib.use('agg')
import numpy             as np
import nibabel           as nib
import scipy.io          as sio
import matplotlib.pyplot as plt
from scipy        import stats, signal
from scipy.sparse import lil_matrix
from rsHRF import spm_dep, processing, canon, sFIR, parameters, basis_functions, utils

import warnings
warnings.filterwarnings("ignore")

def demo_4d_rsHRF(input_file, mask_file, output_dir, para, p_jobs, file_type=".nii", mode='bids'):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    if mode == 'bids':
        name = input_file.filename.split('/')[-1].split('.')[0]
        v = spm_dep.spm.spm_vol(mask_file.filename)
    elif mode == 'bids w/ atlas':
        name = input_file.filename.split('/')[-1].split('.')[0]
        v = spm_dep.spm.spm_vol(mask_file)
    else:
        name = input_file.split('/')[-1].split('.')[0]
        v = spm_dep.spm.spm_vol(mask_file)

    temporal_mask = []
    if 'localK' not in para or para['localK'] == None:
        if para['TR']<=2:
            para['localK'] = 1
        else:
            para['localK'] = 2

    if mode == 'bids' or mode == 'bids w/ atlas':
        v1 = spm_dep.spm.spm_vol(input_file.filename)
    else:
        v1 = spm_dep.spm.spm_vol(input_file)

    if file_type == ".nii" or file_type == ".nii.gz":
        brain = spm_dep.spm.spm_read_vols(v)
    else:
        brain = v.agg_data().flatten(order='F')

    voxel_ind = np.where(brain > 0)[0]

    if ((file_type == ".nii" or file_type == ".nii.gz") and v1.header.get_data_shape()[:-1] != v.header.get_data_shape()) or ((file_type == ".gii" or file_type == ".gii.gz") and v.agg_data().shape[0]!= v.agg_data().shape[0]):
        print('The dimension of your mask is different than '
              'the one of your fMRI data!')
        return
    else:
        if file_type == ".nii" or file_type == ".nii.gz" :
            data = v1.get_data()
            nobs = data.shape[3]         
            mask = v.get_data()
        else:
            data = v1.agg_data()
            N, nobs = data.shape
            mask = v.agg_data()

        data1 = np.reshape(data, (-1, nobs), order='F').T
        bold_sig = stats.zscore(data1[:, voxel_ind], ddof=1)
        bold_sig = np.nan_to_num(bold_sig)
        bold_sig = processing. \
            rest_filter. \
            rest_IdealFilter(bold_sig, para['TR'], para['passband'])
        data_deconv = np.zeros(bold_sig.shape)
        event_number = np.zeros((1, bold_sig.shape[1]))

        print('Retrieving HRF ...')

        if not (para['estimation'] == 'sFIR' or para['estimation'] == 'FIR'):
            #Estimate HRF for the fourier / hanning / gamma / cannon basis functions
            bf = basis_functions.basis_functions.get_basis_function(bold_sig.shape, para)
            beta_hrf, event_bold = utils.hrf_estimation.compute_hrf(bold_sig, para, temporal_mask, p_jobs, bf)
            hrfa = np.dot(bf, beta_hrf[np.arange(0, bf.shape[1]), :])
        else:
            beta_hrf, event_bold = utils.hrf_estimation.compute_hrf(bold_sig, para, temporal_mask, p_jobs)
            hrfa = beta_hrf[:-1,:]

        nvar = hrfa.shape[1]
        PARA = np.zeros((3, nvar))

        for voxel_id in range(nvar):
            hrf1 = hrfa[:, voxel_id]
            PARA[:, voxel_id] = \
                parameters.wgr_get_parameters(hrf1, para['TR'] / para['T'])

        print('Done')

        print('Deconvolving HRF ...')

        if para['T'] > 1:
            hrfa_TR = signal.resample_poly(hrfa, 1, para['T'])
        else:
            hrfa_TR = hrfa

        for voxel_id in range(nvar):
            hrf = hrfa_TR[:, voxel_id]
            H = np.fft.fft(
                np.append(hrf,
                          np.zeros((nobs - max(hrf.shape), 1))), axis=0)
            M = np.fft.fft(bold_sig[:, voxel_id])
            data_deconv[:, voxel_id] = \
                np.fft.ifft(H.conj() * M / (H * H.conj() + .1*np.mean((H * H.conj()))))
            event_number[:, voxel_id] = np.amax(event_bold[voxel_id].shape)

        if mode == 'bids' or mode == 'bids w/ atlas':
            try:
                sub_save_dir = os.path.join(
                    output_dir, 'sub-' + input_file.subject,
                    'session-' + input_file.session,
                    input_file.modality
                )
            except AttributeError as e:
                sub_save_dir = os.path.join(
                    output_dir, 'sub-' + input_file.subject,
                    input_file.modality
                )
        else:
            sub_save_dir = output_dir

        if not os.path.isdir(sub_save_dir):
            os.makedirs(sub_save_dir, exist_ok=True)

        sio.savemat(os.path.join(sub_save_dir, name + '_hrf.mat'),
                    {'para': para, 'hrfa': hrfa,
                     'event_bold': event_bold, 'PARA': PARA})
        HRF_para_str = ['Height', 'Time2peak', 'FWHM']
        mask_data = np.zeros(mask.shape).flatten(order='F')

        for i in range(3):
            fname = os.path.join(sub_save_dir,
                                 name + '_' + HRF_para_str[i])
            mask_data[voxel_ind] = PARA[i, :]
            mask_data = mask_data.reshape(mask.shape, order='F')
            spm_dep.spm.spm_write_vol(v, mask_data, fname, file_type)
            mask_data = mask_data.flatten(order='F')

        fname = os.path.join(sub_save_dir, name + '_event_number.nii')
        mask_data[voxel_ind] = event_number
        mask_data = mask_data.reshape(mask.shape, order='F')
        spm_dep.spm.spm_write_vol(v, mask_data, fname, file_type)

        mask_data = np.zeros(data.shape)
        dat3 = np.zeros(data.shape[:-1]).flatten(order='F')
        for i in range(nobs):
            fname = os.path.join(sub_save_dir, name + '_deconv')
            dat3[voxel_ind] = data_deconv[i, :]
            dat3 = dat3.reshape(data.shape[:-1], order='F')
            if file_type == ".nii" or file_type == ".nii.gz" :
                mask_data[:, :, :, i] = dat3
            else:
                mask_data[:, i] = dat3
            dat3 = dat3.flatten(order='F')
        spm_dep.spm.spm_write_vol(v1, mask_data, fname, file_type)

        event_plot = lil_matrix((1, nobs))
        event_plot[:, event_bold[0]] = 1
        event_plot = np.ravel(event_plot.toarray())

        plt.figure()
        plt.plot(para['TR'] * np.arange(1, np.amax(hrfa[:, 0].shape) + 1),
                 hrfa[:, 0], linewidth=1)
        plt.xlabel('time (s)')
        plt.savefig(os.path.join(sub_save_dir, name + '_plot_1.png'))

        plt.figure()
        plt.plot(para['TR'] * np.arange(1, nobs + 1),
                 np.nan_to_num(stats.zscore(bold_sig[:, 0], ddof=1)),
                 linewidth=1)
        plt.plot(para['TR'] * np.arange(1, nobs + 1),
                 np.nan_to_num(stats.zscore(data_deconv[:, 0], ddof=1)),
                 color='r', linewidth=1)
        markerline, stemlines, baseline = \
            plt.stem(para['TR'] * np.arange(1, nobs + 1), event_plot)
        plt.setp(baseline, 'color', 'k', 'markersize', 1)
        plt.setp(stemlines, 'color', 'k')
        plt.setp(markerline, 'color', 'k', 'markersize', 3, 'marker', 'd')
        plt.legend(['BOLD', 'deconvolved', 'events'])
        plt.xlabel('time (s)')
        plt.savefig(os.path.join(sub_save_dir, name + '_plot_2.png'))

        print('Done')