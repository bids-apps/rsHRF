import numpy as np
from scipy.io   import savemat
from copy       import deepcopy

from .hrf                         import HRF 
from .timeseries                  import TimeSeries
from ...datatypes.misc.parameters import Parameters

class Bold_Deconv(TimeSeries):
    """
    This stores the Deconvolved BOLD Time-series
    
    Attributes:
        1. HRF          : The HRF used to obtain the Deconvolved BOLD
        2. event_num    : The event-numbers
    """
    def __init__(self, label="",ts=np.array([]),subject_index="", para=Parameters()):
        TimeSeries.__init__(self, label="",ts=np.array([]),subject_index="", para=Parameters())
        self.label         = label
        self.subject_index = subject_index
        self.timeseries    = ts
        self.shape         = ts.shape
        self.parameters    = deepcopy(para) 
        self.HRF           = HRF()
        self.event_num     = np.array([])
    
    #setters
    def set_HRF(self, HRF):
        self.HRF = HRF 
    def set_event_num(self, ev):
        self.event_num = ev 
    
    #getters
    def get_event_num(self):
        return self.event_num
    def get_associated_HRF(self):
        return self.HRF 
    
    #misc
    def compareTimeSeries(self, ts):
        """ Compares another time-series with itself to determine if both are identical 
            Two checks are performed:
                1. Label
                2. HRF
            If all the three comparisions return true, then both the HRF
                time-series objects are identical
        """
        if self.label == ts.get_label() \
            and self.HRF.compareTimeSeries(ts.get_associated_HRF()):
            return True 
        else:
            return False
    def save_info(self, name):
        """ Saves the information about the time-series in a .mat file """
        dic = {}
        dic["timeseries"] = self.timeseries
        dic["eventNum"]   = self.event_num
        para              = self.parameters.get_parameters()
        for each in para.keys():
            dic[each] = para[each] 
        savemat(name, dic)
        return True