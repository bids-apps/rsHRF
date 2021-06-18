import os
import numpy    as np
import nibabel  as nib
import scipy.io as sio
from bids.grabbids  import BIDSLayout
from scipy          import stats, signal
from scipy.sparse   import lil_matrix
from ...            import spm_dep, processing, parameters, basis_functions, utils

from ..datatypes.timeseries.hrf               import HRF
from ..datatypes.timeseries.bold_raw          import BOLD_Raw
from ..datatypes.timeseries.bold_preprocessed import BOLD_Preprocessed
from ..datatypes.timeseries.bold_deconv       import Bold_Deconv
from ..datatypes.misc.parameters              import Parameters
from ..datatypes.misc.subject                 import Subject
from ..datatypes.misc.store                   import Store
from ..misc.status                            import Status

import warnings
warnings.filterwarnings("ignore")

class Core():
    """
    All of the processing occurs here
    """
    def __init__(self):
        # constructor
        self.parameters = Parameters() # rsHRF parameters
        self.dataStore  = Store()      # stores the information for the subjects

    # getters for data-store
    def updateParameters(self, dic={}):  
        # updates the rsHRF-parameters   
        return self.parameters.set_parameters(dic) 

    def get_parameters(self):
        # returns the rsHRF-parameters
        return self.parameters.get_parameters()    

    def get_time_series(self, curr):
        # gets the time-series
        return self.dataStore.get_time_series(curr)

    def get_plotables(self, curr):
        # gets all the time-series objects that can be plotted
        return self.dataStore.get_plotables(curr)

    def get_store_info(self, curr):
        # gets the information regarding the time-series objects
        return self.dataStore.get_info(curr)

    def get_subjects(self):
        # gets all the subjects present in the data-store
        return self.dataStore.get_subjects()
    
    def get_data_labels(self, curr):
        # gets all the labels present in the data-store
        return self.dataStore.get_data_labels(curr)

    # saving data
    def save_info(self, curr, out):
        return self.dataStore.save_info(curr, out)
    
    def makeInput(self, inp):
        """
        Obtains the input (file-paths and input-mode) from the main window
        and updates the subjects/time-series objects appropriately
        """
        # obtains the Raw BOLD data and preprocessed data, and updates the data-store
        input_file, mask_file, file_type, mode = inp # each input comprises of an input_file, mask_file and a file_type, and the mode 
        if mode == "file":                           # if the mode is file (that is input is a stand-alone NIfTI or GIfTI file)
            return self.makeInputFile(input_file, mask_file, file_type, 'file')
        # if the input is present in a directory organized in BIDS format
        elif "bids" in mode:
            # obtaining all the input files
            layout              = BIDSLayout(input_file)
            subjects_to_analyze = layout.get_subjects()
            # if no subjects were found
            if not subjects_to_analyze:
                return Status(False, error='Could not find participants. Please make sure the BIDS data '
                         'structure is present and correct. Datasets can be validated online '
                         'using the BIDS Validator (http://incf.github.io/bids-validator/).')
            all_inputs = layout.get(modality='func', subject=subjects_to_analyze, task='rest', type='preproc', extensions=['nii', 'nii.gz'])
            # if no *preproc.nii or *preproc.nii.gz files were found
            if not all_inputs != []:
                return Status(False, error = 'There are no files of type *preproc.nii / *preproc.nii.gz '
                         'Please make sure to have at least one file of the above type '
                         'in the BIDS specification')
            # if the atlas file is provided
            if mode == "bids w/ atlas":
                for file_count in range(len(all_inputs)):
                    # making input for every combination of input-file and atlas
                    temp = (self.makeInputFile(all_inputs[file_count], mask_file, ".nii", 'bids w/ atlas'))
                    if not temp.get_state():
                        return temp 
                # returns the status
                return Status(True, info="Preprocessed all input", dic={"Number of Input Subjects: ":len(all_inputs)})
            # if the atlas file is not provided
            elif mode == "bids":
                # obtaining the masks
                all_masks = layout.get(modality='func', subject=subjects_to_analyze, task='rest', type='brainmask', extensions=['nii', 'nii.gz'])
                # if no mask files were found
                if not all_masks != []:
                    return Status(False, error='There are no files of type *brainmask.nii / *brainmask.nii.gz '
                             'Please make sure to have at least one file of the above type '
                             'in the BIDS specification')
                # if the number of mask files != number of input files
                if len(all_inputs) != len(all_masks):
                    return Status(False, error='The number of *preproc.nii / .nii.gz and the number of '
                                 '*brainmask.nii / .nii.gz are different. Please make sure that '
                                 'there is one mask for each input_file present')
                all_inputs.sort()
                all_masks.sort()
                # matching the prefix to align the inputs and the masks together
                all_prefix_match   = False
                prefix_match_count = 0
                for i in range(len(all_inputs)):
                    input_prefix    = all_inputs[i].filename.split('/')[-1].split('_preproc')[0]
                    mask_prefix     = all_masks[i].filename.split('/')[-1].split('_brainmask')[0]
                    if input_prefix == mask_prefix:
                        prefix_match_count += 1
                    else:
                        all_prefix_match = False
                        break
                if prefix_match_count == len(all_inputs):
                    all_prefix_match  = True
                # if the mask and input files have different prefix
                if not all_prefix_match:
                    return Status(False, error='The mask and input files should have the same prefix for correspondence. '
                                 'Please consider renaming your files')
                else:
                    # making input for every combination of input-file and mask-file
                    for file_count in range(len(all_inputs)):
                        temp = (self.makeInputFile(all_inputs[file_count], all_masks[file_count], ".nii", 'bids'))
                        if not temp.get_state():
                            return temp 
                    # returns the status
                    return Status(True, info="Preprocessed all input", dic={"Number of Input Subjects: ":len(all_inputs)})

    def makeInputFile(self, input_file, mask_file, file_type, mode):
        """
        Obtains the Raw BOLD Time-series and Preprocessed BOLD Time-series
        when the input is a stand-alone NIfTI or GIfTI file
        """
        # if the input is in form of a File object
        if 'bids' in mode:
            input_file = input_file.filename
        # if the mask is in form of a File object
        if mode == 'bids':
            mask_file = mask_file.filename
        # getting the subject index
        try:
            subject_index =  input_file.split("/")[-1].split("_")[0][4:]
        except:
            return Status(False, error="Input file should begin with 'sub-'")
        # obtaining the header for the mask
        try:  
            v    = spm_dep.spm.spm_vol(mask_file)
        except :
            return Status(False, error="Invalid Mask File!")
        # obtaining the header for the input
        try:   
            v1   = spm_dep.spm.spm_vol(input_file)
        except: 
            return Status(False, error="Invalid Input File!")
        # obtaining the mask data
        if file_type   == ".nii" or file_type == ".nii.gz":
            brain       = spm_dep.spm.spm_read_vols(v)
        elif file_type == ".gii" or file_type == ".gii.gz":
            brain       = v.agg_data().flatten(order='F')
        else:
            return Status(False, error="Invalid Input File Type!")
        # brain voxel indices with as obtained by mask-data
        voxel_ind = np.where(brain > 0)[0]
        # checking the dimensions of the mask-file and input-file
        if ((file_type == ".nii" or file_type == ".nii.gz") and v1.header.get_data_shape()[:-1] != v.header.get_data_shape()) or ((file_type == ".gii" or file_type == ".gii.gz") and v.agg_data().shape[0]!= v.agg_data().shape[0]):
            return Status(False, error='The dimension of your mask is different than the one of your fMRI data!')
        # checking whether the subject is already present in the datastore
        if not self.dataStore.is_present(subject_index):
            # instantiating a new object if it is not present
            subject = Subject(index=subject_index)
            self.dataStore.add_subject(subject)
        else:
            # obtaining the object if it is present
            subject = self.dataStore.get_subject_by_index(subject_index)
        # checks if the BOLD time-series is already present
        if not subject.is_present("BOLD", input_file):   # if the time-series is not present
            if file_type   == ".nii" or file_type == ".nii.gz" :
                data            = v1.get_data()                 
                nobs            = data.shape[3]
                data1           = np.reshape(data, (-1, nobs), order='F').T
            elif file_type == ".gii" or file_type == ".gii.gz":
                data            = v1.agg_data()
                _, nobs         = data.shape
                data1           = np.reshape(data, (-1, nobs), order='F').T    
            bold_ts             = BOLD_Raw(label="BOLD", ts=np.array(data1), para=self.parameters, subject_index=subject.get_subject_index())   
            bold_ts.set_inputfile(input_file)   # the Raw BOLD Time-series is associated to a particular input-file 
            subject.add_BOLD_raw(bold_ts)       # adding the time-series object
        else:
            bold_ts             = subject.is_present("BOLD", input_file, getts=True)
        data1                   = bold_ts.get_ts()
        # checks if the Preprocessed-BOLD time-series is already present
        if not subject.is_present("Preprocessed-BOLD", (self.parameters, mask_file, bold_ts)):
            # pre-processing the time-series
            bold_sig = stats.zscore(data1[:, voxel_ind], ddof=1)
            bold_sig = np.nan_to_num(bold_sig)
            # instantiating the time-series objects
            bold_pre_ts = BOLD_Preprocessed(label="Preprocessed-BOLD", ts=np.array(bold_sig), para=self.parameters, subject_index=subject.get_subject_index())
            bold_pre_ts.set_BOLD_Raw(bold_ts)   # the Preprocessed BOLD Time-series is associated to a particular Raw BOLD Time-Series
            bold_pre_ts.set_maskfile(mask_file) # and a particular mask_file
            subject.add_BOLD_pre(bold_pre_ts)   # adding the time-series objects
            # returning the status
            return Status(True, info="Preprocessed Input!", dic={"Number of Time-Slices: ": bold_ts.get_shape()[0], "Number of Brain-Voxels: ":bold_ts.get_shape()[1]})
        return Status(False, error="Time series already exists. No new additions were made.")

    def retrieveHRF(self, bold_pre_ts, get_pos=False):
        """
        Retrieves the resting-state Hemodynamic Response Function
        with Preprocessed BOLD Time-series as input, and self.parameters
        as the parameters
        """
        subject_index = bold_pre_ts.get_subject_index()                    # gets the subject-index associated to the preprocessed BOLD Time-series
        subject       = self.dataStore.get_subject_by_index(subject_index) # gets the subject from the index
        # if the HRF has already been retrieved for this particular set of inputs
        if not subject.is_present("HRF", (self.parameters, bold_pre_ts)): 
            # inputs for retrieving the HRF
            bold_sig  = bold_pre_ts.get_ts()
            bold_sig  = processing. \
                        rest_filter. \
                        rest_IdealFilter(bold_sig, self.parameters.get_TR(), self.parameters.get_passband_deconvolve())
            para      = self.parameters.get_parameters()
            if not (para['estimation'] == 'sFIR' or para['estimation'] == 'FIR'):
                # estimate HRF for the fourier / hanning / gamma / cannon basis functions
                bf = basis_functions.basis_functions.get_basis_function(bold_sig.shape, para)       # obtaining the basis set
                beta_hrf, event_bold = utils.hrf_estimation.compute_hrf(bold_sig, para, [], -1, bf)
                hrfa = np.dot(bf, beta_hrf[np.arange(0, bf.shape[1]), :])
            else:
                # estimate HRF for FIR and sFIR
                beta_hrf, event_bold = utils.hrf_estimation.compute_hrf(bold_sig, para, [], -1)
                hrfa = beta_hrf
            # instantiating the time-series objects
            hrf = HRF(label="HRF", ts=hrfa, subject_index=subject_index, para=self.parameters)
            hrf.set_BOLD(bold_pre_ts)      # the HRF is associated to a particular Preprocessed BOLD Time-series
            hrf.set_event_bold(event_bold) # setting the bold-events
            pos = subject.add_HRF(hrf)     # adding the HRF to the subject
            # returning the status
            if get_pos:
                return Status(True, info="Retrieved HRF!", dic={"Shape of HRF: ": hrf.get_shape()}), pos
            else:
                return  Status(True, info="Retrieved HRF!", dic={"Shape of HRF: ": hrf.get_shape()})
        if get_pos:
            return Status(False, error="Time series already exists. No new additions were made."), None
        else:
            return Status(False, error="Time series already exists. No new additions were made.")

    def getHRFParameters(self, hrf):
        """
        Retrieves the resting-state Hemodynamic Response Function Parameters
        with HRF as input, and self.parameters as the parameters
        """
        # checking if the parameters have already been computed for HRF
        if hrf.get_HRF_para().size != 0:
            return Status(False,error="Parameters have already been computed for this HRF")
        # inputs for obtaining the parameters
        hrfa    = hrf.get_ts()
        para    = hrf.get_parameters().get_parameters()
        nvar    = hrfa.shape[1]
        PARA    = np.zeros((3, nvar))
        average = [0 for i in range(3)]
        # obtaining the parameters for each voxel
        for voxel_id in range(nvar):
            hrf1              = hrfa[:, voxel_id]
            PARA[:, voxel_id] = parameters.wgr_get_parameters(hrf1, para['TR'] / para['T'])
            for i in range(3):
                average[i] += PARA[i, voxel_id] 
        for i in range(3):
            average[i] /= nvar
        # setting the parameters
        hrf.set_para(PARA)
        # returning the status
        return Status(True, info="Retrieved HRF Parameters", dic={"Average Height: ":str(average[0])[:3], \
         "Avearage Time-To-Peak: ": str(average[1])[:3] + " seconds", "Avearge Full-Width at Half-Max: ": str(average[2])[:3]})

    def deconvolveHRF(self, hrf):
        """
        Retrieves the Deconvolved BOLD Time-series
        with HRF as input, and self.parameters as the parameters
        """
        subject_index = hrf.get_subject_index()                                     # gets the subject-index associated to the preprocessed BOLD Time-series
        subject       = self.dataStore.get_subject_by_index(subject_index)          # gets the subject from the index
        para          = self.parameters.get_parameters()    
        # if the HRF has already been retrieved for this particular set of inputs
        if not subject.is_present("Deconvolved-BOLD", (self.parameters, hrf)): 
            # inputs for retrieving the deconvolved BOLD
            hrfa              = hrf.get_ts()
            bold_sig          = hrf.get_associated_BOLD().get_ts()
            bold_sig          = processing. \
                                rest_filter. \
                                rest_IdealFilter(bold_sig, self.parameters.get_TR(), self.parameters.get_passband_deconvolve())
            event_bold        = hrf.get_event_bold()
            nvar              = hrfa.shape[1]
            nobs              = bold_sig.shape[0]
            data_deconv       = np.zeros(bold_sig.shape)
            event_number      = np.zeros((1, bold_sig.shape[1]))
            if para['T'] > 1:
                hrfa_TR = signal.resample_poly(hrfa, 1, para['T'])
            else:
                hrfa_TR = hrfa
            # obtaining the deconvolved BOLD for each voxel
            for voxel_id in range(nvar):
                hrf_                       = hrfa_TR[:, voxel_id]
                H                          = np.fft.fft(np.append(hrf_, np.zeros((nobs - max(hrf_.shape), 1))), axis=0)
                M                          = np.fft.fft(bold_sig[:, voxel_id])
                data_deconv[:, voxel_id]   = np.fft.ifft(H.conj() * M / (H * H.conj() + .1*np.mean((H * H.conj()))))
                event_number[:, voxel_id]  = np.amax(event_bold[voxel_id].shape)
            # instantiating the time-series object
            dd = Bold_Deconv(label="Deconvolved-BOLD", ts=data_deconv,subject_index=subject_index, para=hrf.get_parameters())
            dd.set_HRF(hrf) # the deconvoled BOLD Time-series is associated to a particular HRF
            dd.set_event_num(event_number) # setting the BOLD events
            pos = subject.add_BOLD_deconv(dd) # adding the time-series to the subject
            # returning the status
            return Status(True, info="Deconvolved BOLD Signal")
        return Status(False, error="Time series already exists. No new additions were made.")