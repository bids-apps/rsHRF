import numpy as np
from scipy.io   import savemat
from copy       import deepcopy

from ...datatypes.misc.parameters import Parameters
from .timeseries                  import TimeSeries

class HRF(TimeSeries):
    """
    This stores the Hemodynamic Response Function Time-series
    
    Attributes:
        1. BOLD       = stores the associated Preprocessed-BOLD time-series object through which it was retrieved
        2. PARA       = stores the HRF parameters (Full-width at half-max, Time-to-peak and height)
        3. event_bold = stores the bold-events
    """
    def __init__(self, label="",ts=np.array([]),subject_index="", para=Parameters()):
        TimeSeries.__init__(self, label="",ts=np.array([]),subject_index="", para=Parameters())
        self.label           = label
        self.subject_index   = subject_index
        self.timeseries      = ts
        self.shape           = ts.shape
        self.parameters      = deepcopy(para)
        self.BOLD            = TimeSeries()
        self.PARA            = np.array([])
        self.event_bold      = np.array([])
    
    # setters
    def set_para(self, PARA):
        self.PARA = PARA 

    def set_BOLD(self, BOLD):
        self.BOLD = BOLD 

    def set_event_bold(self, event_bold):
        self.event_bold = event_bold 
    
    # getters
    def get_event_bold(self):
        return self.event_bold

    def get_associated_BOLD(self):
        return self.BOLD 

    def get_HRF_para(self):
        return self.PARA 

    # misc.
    def compareTimeSeries(self, ts):
        """ Compares whether another HRF time-series is similar to it.
            Three checks are performed for this:
                1. Label
                2. rsHRF Parameters
                3. Preprocessed-BOLD which was used as input
            If all the three comparisions return true, then both the HRF
                time-series objects are identical 
        """
        if self.label == ts.get_label() and self.parameters.compareParameters(ts.get_parameters()) and self.BOLD.compareTimeSeries(ts.get_associated_BOLD()):
            return True 
        else:
            return False

    def save_info(self, name):
        """ Saves the information about the time-series in a .mat file """
        try:
            dic = {}
            dic["timeseries"] = self.timeseries
            dic["PARA"] = self.PARA 
            dic["eventBold"] = self.event_bold
            para = self.parameters.get_parameters()
            for each in para.keys():
                dic[each] = para[each] 
            savemat(name, dic)
            return True
        except:
            return False