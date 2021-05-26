import numpy as np
from copy import deepcopy

from ...datatypes.misc.parameters import Parameters

class TimeSeries():
    """ 
    Deals with all the time-series artifacts that appear during the processing.

    These are the various time-series that are dealt with:
        1. BOLD              : (Raw BOLD Data)
        2. HRF               : (Hemodynamic Response Function)
        3. Preprocessed-BOLD : (Z-score and Passband filtered)
        4. Deconvolved-BOLD  : (Deconvolved using the HRF)

    Attributes:
        1. label         : Takes on one of the values as described above
        2. subject_index : index of the subject to which the current time-series belongs
        3. timeseries    : stores the time-series as a 2-dimensional numpy array
        4. shape         : shape of the time-series (voxels x time-slices)
        5. parameters    : rsHRF-parameters associated in retrieving this time-series
    """
    def __init__(self, label="",subject_index="",ts=np.array([]), para=Parameters()):
        self.label          = label
        self.subject_index  = subject_index
        self.timeseries     = deepcopy(ts)
        self.shape          = ts.shape
        self.parameters     = deepcopy(para) 
    
    # setters
    def set_ts(self, ts):
        self.timeseries     = deepcopy(ts) 
        self.shape          = self.timeseries.shape
    
    def set_parameters(self,para):
        self.parameters     = deepcopy(para) 
    
    def set_label(self,label):
        self.label          = label 
    
    def set_subject_index(self,subject_index):
        self.subject_index  = subject_index
    
    # getters
    def get_ts(self):
        return self.timeseries
    
    def get_subject_index(self):
        return self.subject_index
    
    def get_label(self):
        return self.label 
    
    def get_parameters(self):
        return self.parameters
    
    def get_shape(self):
        return self.shape 
    
    # misc.
    def get_info(self):
        """ Returns the information about the time-series in the form of a dictionary """
        dic                      = {}
        dic["Type"]              = self.label
        dic["Subject"]           = self.subject_index
        dic["Time Series Shape"] = self.shape
        dic["Parameters"]        = self.parameters.get_parameters()
        return dic

    def compareTimeSeries(self, ts):
        """ Compares another time-series with itself to determine if both are identical """
        raise NotImplementedError("This needs to be overridden in the child-classes")

    def save_info(self, name):
        """ Saves the information about the time-series in a .mat file """
        raise NotImplementedError("This needs to be overridden in the child-classes")

