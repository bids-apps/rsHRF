import numpy as np
from copy import deepcopy
from datatypes.misc.parameters import Parameters
from .timeseries import TimeSeries
import scipy.io

class HRF(TimeSeries):
    def __init__(self, label="",ts=np.array([]),subject_index="", para=Parameters()):
        TimeSeries.__init__(self, label="",ts=np.array([]),subject_index="", para=Parameters())
        self.label = label
        self.subject_index = subject_index
        self.timeseries = deepcopy(ts)
        self.shape = ts.shape
        self.parameters = deepcopy(para) 
        self.BOLD = TimeSeries()
        self.PARA = np.array([])
        self.event_bold = np.array([])
    
    def set_para(self, PARA):
        self.PARA = PARA 
    def set_BOLD(self, BOLD):
        self.BOLD = BOLD 
    def set_event_bold(self, event_bold):
        self.event_bold = event_bold 
    def get_event_bold(self):
        return self.event_bold
    def get_associated_BOLD(self):
        return self.BOLD 
    def get_HRF_para(self):
        return self.PARA 
    def compareTimeSeries(self, ts):
        if self.label == ts.get_label() and self.parameters.compareParameters(ts.get_parameters()) and self.BOLD.compareTimeSeries(ts.get_associated_BOLD()):
            return True 
        else:
            return False
    def save_info(self, name):
        dic = {}
        dic["timeseries"] = self.timeseries
        dic["PARA"] = self.PARA 
        dic["eventBold"] = self.event_bold
        para = self.parameters.get_parameters()
        for each in para.keys():
            dic[each] = para[each] 
        scipy.io.savemat(name, dic)
        return True