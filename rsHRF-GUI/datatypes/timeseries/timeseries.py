import scipy.io
import numpy as np
from copy import deepcopy
from datatypes.misc.parameters import Parameters

''' 
These are the various time-series that are dealt:
    1. BOLD              (Raw Data)
    2. HRF               (Hemodynamic Response Function)
    3. Preprocessed-BOLD (Z-score and Passband filtered)
    4. Deconvolved-BOLD  (Deconvolved using the HRF)
'''
class TimeSeries():
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
    
    # to compare between two time-series object of the same subject
    def compareTimeSeries(self, ts):
        if self.label == ts.get_label() and self.parameters.compareParameters(ts.get_parameters()):
            return True 
        else:
            return False
    
    # get information regarding the time-series
    def get_info(self):
        dic = {}
        dic["Type"] = self.label
        dic["Subject"] = self.subject_index
        dic["Time Series Shape"] = self.shape
        dic["Parameters"] = self.parameters.get_parameters()
        return dic
    
    # saving the time-series information as a .mat file
    def save_info(self, name):
        dic = {}
        dic["timeseries"] = self.timeseries
        para = self.parameters.get_parameters()
        for each in para.keys():
            dic[each] = para[each] 
        scipy.io.savemat(name, dic)
        return True