import os
import numpy    as np
import nibabel  as nib
import scipy.io as sio
from scipy        import stats, signal
from scipy.sparse import lil_matrix

from datatypes.timeseries.hrf import HRF
from datatypes.timeseries.timeseries import TimeSeries
from datatypes.timeseries.bold_deconv import Bold_Deconv
from datatypes.misc.parameters import Parameters
from datatypes.misc.subject import Subject
from misc.status import Status
from rsHRF       import spm_dep, processing, canon, sFIR, parameters, basis_functions, utils, fourD_rsHRF

import warnings
warnings.filterwarnings("ignore")

class Core():
    def __init__(self, dataStore):
        self.parameters = Parameters()
        self.dataStore  = dataStore

    def updateParameters(self, dic={}):     
        return self.parameters.set_parameters(dic)

    def get_parameters(self):
        return self.parameters.get_parameters()
    
    def makeInput(self, inp, choice=None):
        input_file, mask_file, file_type, mode = inp
        if mode == "file":
            return self.makeInputFile(input_file, mask_file, file_type)
        elif mode == "bids w/ atlas":
            try:
                if not os.path.isdir(input_file):
                    return Status(False, error="Input is not a valid directory")
            except:
                return Status(False, error="Input is not a valid directory")
            subjects = os.listdir(input_file)
            subs     = []
            masks    = []
            for i in range(len(subjects)):
                if subjects[i][:4] == "sub-":
                    temp = input_file + "/" + subjects[i] + "/func/" + subjects[i] + "_task-rest_bold"
                    if os.path.isfile(temp+".nii"):
                        subs.append(temp+".nii")
                    elif os.path.isfile(temp+".nii.gz"):
                        subs.append(temp+".nii.gz")
                    elif os.path.isfile(temp+".gii"):
                        subs.append(temp+".gii")
                    elif os.path.isfile(temp+".gii.gz"):
                        subs.append(temp+".gii.gz")
                    if os.path.isfile(temp+"_mask.nii"):
                        masks.append(temp+"_mask.nii")
                    elif os.path.isfile(temp+"_mask.nii.gz"):
                        masks.append(temp+"_mask.nii.gz")
                    elif os.path.isfile(temp+"_mask.gii"):
                        masks.append(temp+"_mask.gii")
                    elif os.path.isfile(temp+"_mask.gii.gz"):
                        masks.append(temp+"_mask.gii.gz")
                    else:
                        continue
            if len(masks) != len(subs):
                return Status(False, error="Inconsistent number of data and mask files")
            for i in range(len(subs)):
                file_type = "." + subs[i].split('.',1)[1]
                status = self.makeInputFile(subs[i],masks[i], file_type)
                if not status.get_state() :
                    return status
            return Status(True, info="Preprocessed all input", dic={"Number of Input Subjects: ":str(len(subs))})
        elif mode == "bids":
            try:
                if not os.path.isdir(input_file):
                    return Status(False, error="Input is not a valid directory")
            except:
                return Status(False, error="Input is not a valid directory")
            subjects = os.listdir(input_file)
            subs     = []
            for i in range(len(subjects)):
                if subjects[i][:4] == "sub-":
                    temp = input_file + "/" + subjects[i] + "/func/" + subjects[i] + "_task-rest_bold"
                    if os.path.isfile(temp+".nii"):
                        subs.append(temp+".nii")
                    elif os.path.isfile(temp+".nii.gz"):
                        subs.append(temp+".nii.gz")
                    elif os.path.isfile(temp+".gii"):
                        subs.append(temp+".gii")
                    elif os.path.isfile(temp+".gii.gz"):
                        subs.append(temp+".gii.gz")
            for i in range(len(subs)):
                file_type = "." + subs[i].split('.',1)[1]
                status    = self.makeInputFile(subs[i],mask_file, file_type)
                if not status.get_state() :
                    return status
            return Status(True, info="Preprocessed all input", dic={"Number of Input Subjects: ":str(len(subs))})
            

    def makeInputFile(self, input_file, mask_file, file_type):
        try:  
            v    = spm_dep.spm.spm_vol(mask_file)
        except :
            return Status(False, error="Invalid Mask File!")
        try:   
            v1   = spm_dep.spm.spm_vol(input_file)
        except: 
            return Status(False, error="Invalid Input File!")
        if file_type == ".nii" or file_type == ".nii.gz":
            brain = spm_dep.spm.spm_read_vols(v)
        else:
            brain = v.agg_data().flatten(order='F')
        voxel_ind = np.where(brain > 0)[0]
        if ((file_type == ".nii" or file_type == ".nii.gz") and v1.header.get_data_shape()[:-1] != v.header.get_data_shape()) or ((file_type == ".gii" or file_type == ".gii.gz") and v.agg_data().shape[0]!= v.agg_data().shape[0]):
            error = 'The dimension of your mask is different than the one of your fMRI data!'
            return Status(False, error=error)
        else:
            # creating a new subject
            new_subject     = self.dataStore.get_subject(input_file, mask_file)
            if new_subject == None:
                new_subject = Subject(input_filename=input_file,mask_filename=mask_file)
                self.dataStore.add_subject(new_subject)
            bold_ts = new_subject.get_time_series(TimeSeries(label="BOLD", para=self.parameters))
            if bold_ts == None:  
                if file_type == ".nii" or file_type == ".nii.gz" :
                    data            = v1.get_data()
                    nobs            = data.shape[3]
                    data1           = np.reshape(data, (-1, nobs), order='F').T
                    bold_sig        = stats.zscore(data1[:, voxel_ind], ddof=1)
                    mask            = v.get_data()
                else:
                    data            = v1.agg_data()
                    _, nobs         = data.shape
                    data1           = np.reshape(data, (-1, nobs), order='F').T      
                    bold_sig        = stats.zscore(data1[:, voxel_ind], ddof=1)  
                    mask            = v.agg_data()
                passband = list(self.parameters.get_passband())
                bold_sig = np.nan_to_num(bold_sig)
                bold_sig = processing. \
                    rest_filter. \
                    rest_IdealFilter(bold_sig, self.parameters.get_TR(), self.parameters.get_passband())
                bold_ts = TimeSeries(label="BOLD", ts=np.array(data1), para=self.parameters, subject_index=new_subject.get_subject_index())
                bold_pre_ts = TimeSeries(label="Preprocessed-BOLD",ts=np.array(bold_sig),para=self.parameters, subject_index=new_subject.get_subject_index())
                new_subject.add_BOLD(bold_ts)
                new_subject.add_BOLD_pre(bold_pre_ts)
                return Status(True, info="Preprocessed Input!", dic={"Number of Time-Slices: ": nobs, "Number of Brain-Voxels: ":bold_ts.get_shape()[1]})
            else:
                return Status(False, error="Time series already exists. No new additions were made.")

    def retrieveHRF(self, bold_ts):
        subject_index = bold_ts.get_subject_index()
        subject       = self.dataStore.get_subject_by_index(subject_index)
        hrfa          = HRF(label="HRF",para=self.parameters)
        hrfa.set_BOLD(bold_ts)
        hrfa          = subject.get_time_series(hrfa)
        if hrfa == None:
            bold_sig = bold_ts.get_ts()
            para     = self.parameters.get_parameters()
            if bold_sig.size == 0:
                return Status(False, error="BOLD Input has size = 0")
            bold_sig                       = bold_sig[:,:3] # confining it to 3 voxels for analysis
            beta_hrf, event_bold, bf       = utils.hrf_estimation.compute_hrf(bold_sig, para, [], 1)
            if not (para['estimation'] == 'sFIR' or para['estimation'] == 'FIR'):
                hrfa = np.dot(bf, beta_hrf[np.arange(0, bf.shape[1]), :])
            else:
                hrfa = beta_hrf
            hrf = HRF(label="HRF",para=self.parameters)
            hrf.set_BOLD(bold_ts)
            hrf.set_ts(hrfa)
            hrf.set_event_bold(event_bold)
            hrf.set_subject_index(bold_ts.get_subject_index())
            subject.add_HRF(hrf)
            return Status(True, info="Retrieved HRF!", dic={"Shape of HRF: ": hrf.get_shape()})
        else:
            return Status(False, error="Time series already exists. No new additions were made.")

    def getHRFParameters(self, hrf):
        if hrf.get_HRF_para().size != 0:
            return Status(False,error="Parameters have already been computed for this HRF")
        hrfa = hrf.get_ts()
        if hrfa.size == 0:
            return Status(False,error="HRF Input has size = 0")
        para = hrf.get_parameters().get_parameters()
        nvar = hrfa.shape[1]
        PARA = np.zeros((3, nvar))
        average = [0 for i in range(3)]
        for voxel_id in range(nvar):
            hrf1              = hrfa[:, voxel_id]
            PARA[:, voxel_id] = parameters.wgr_get_parameters(hrf1, para['TR'] / para['T'])
            for i in range(3):
                average[i] += PARA[i, voxel_id] 
        for i in range(3):
            average[i] /= nvar
        hrf.set_para(PARA)
        return Status(True, info="Retrieved HRF Parameters", dic={"Average Height: ":str(average[0])[:3], \
         "Avearage Time-To-Peak: ": str(average[1])[:3] + " seconds", "Avearge Full-Width at Half-Max: ": str(average[2])[:3]})

    def deconvolveHRF(self, hrf):
        subject_index = hrf.get_subject_index()
        subject       = self.dataStore.get_subject_by_index(subject_index)
        data_deconv   = Bold_Deconv(label="Deconvolved-BOLD",para=hrf.get_parameters())
        data_deconv.set_HRF(hrf)
        dd = subject.get_time_series(data_deconv)
        if dd == None:
            hrfa       = hrf.get_ts()
            bold_sig   = hrf.get_associated_BOLD().get_ts()
            para       = hrf.get_parameters().get_parameters()
            event_bold = hrf.get_event_bold()
            if hrfa.size == 0:
                return Status(False, error="HRF Input has size = 0")
            nvar              = hrfa.shape[1]
            nobs              = bold_sig.shape[0]
            data_deconv       = np.zeros(bold_sig.shape)
            event_number      = np.zeros((1, bold_sig.shape[1]))
            if para['T'] > 1:
                hrfa_TR = signal.resample_poly(hrfa, 1, para['T'])
            else:
                hrfa_TR = hrfa
            for voxel_id in range(nvar):
                hrf_ = hrfa_TR[:, voxel_id]
                H    = np.fft.fft(np.append(hrf_, np.zeros((nobs - max(hrf_.shape), 1))), axis=0)
                M    = np.fft.fft(bold_sig[:, voxel_id])
                data_deconv[:, voxel_id]   = np.fft.ifft(H.conj() * M / (H * H.conj() + .1*np.mean((H * H.conj()))))
                event_number[:, voxel_id]  = np.amax(event_bold[voxel_id].shape)
            dd = Bold_Deconv(label="Deconvolved-BOLD",para=hrf.get_parameters())
            dd.set_HRF(hrf)
            dd.set_ts(data_deconv)
            dd.set_event_num(event_number)
            dd.set_subject_index(hrf.get_subject_index())
            subject.add_BOLD_deconv(dd)
            return Status(True, info="Deconvolved BOLD Signal")
        else:
            return Status(False, error="Time series already exists. No new additions were made.")