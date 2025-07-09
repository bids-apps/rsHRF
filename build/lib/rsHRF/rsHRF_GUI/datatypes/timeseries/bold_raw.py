import numpy as np
from scipy.io   import savemat
from copy       import deepcopy

from ...datatypes.misc.parameters import Parameters 
from .timeseries                  import TimeSeries

class BOLD_Raw(TimeSeries):
    """
    This stores the Raw BOLD Time-series
    
    Attributes:
        1. input_file : the input-file path of the Raw BOLD Time-series
    """
    def __init__(self, label="",ts=np.array([]),subject_index="", para=Parameters()):
        TimeSeries.__init__(self, label="",ts=np.array([]),subject_index="", para=Parameters())
        self.label          = label 
        self.subject_index  = subject_index 
        self.timeseries     = ts 
        self.shape          = ts.shape
        self.parameters     = deepcopy(para) 
        self.input_file     = ""

    # setters
    def set_inputfile(self, input_file):
        self.input_file = input_file

    # getters
    def get_inputfile(self):
        return self.input_file

    # misc.
    def compareTimeSeries(self, ts):
        """ Compares another time-series with itself to determine if both are identical 
            Two checks are performed:
                1. Label
                2. Input-file name
            If all the three comparisions return true, then both the HRF
                time-series objects are identical
        """
        if self.label == ts.get_label() and self.input_file == ts.get_inputfile():
            return True 
        else:
            return False 

    def save_info(self, name):
        """ Saves the information about the time-series in a .mat file """
        try:
            dic = {}
            dic["timeseries"] = self.timeseries
            dic["input_file"] = self.input_file 
            savemat(name, dic)
            return True
        except:
            return False
