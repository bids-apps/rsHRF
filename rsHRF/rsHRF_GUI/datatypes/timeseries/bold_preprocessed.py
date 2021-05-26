import numpy as np
from scipy.io   import savemat
from copy       import deepcopy

from ...datatypes.misc.parameters import Parameters 
from .timeseries                  import TimeSeries
from .bold_raw                    import BOLD_Raw

class BOLD_Preprocessed(TimeSeries):
    """
    This stores the Preprocessed BOLD Time-series
    
    Attributes:
        1. BOLD_Raw     : The Raw BOLD time-series object through which it was derived
        2. mask_file    : The mask-file path
    """
    def __init__(self, label="",ts=np.array([]),subject_index="", para=Parameters()):
        TimeSeries.__init__(self, label="",ts=np.array([]),subject_index="", para=Parameters())
        self.label          = label 
        self.subject_index  = subject_index 
        self.timeseries     = ts 
        self.shape          = ts.shape
        self.parameters     = deepcopy(para) 
        self.BOLD_Raw       = BOLD_Raw()
        self.mask_file      = ""

    # setters
    def set_maskfile(self, mask_file):
        self.mask_file = mask_file 

    def set_BOLD_Raw(self, BOLD_Raw):
        self.BOLD_Raw = BOLD_Raw
    
    # getters
    def get_maskfile(self):
        return self.mask_file 

    def get_BOLD_Raw(self):
        return self.BOLD_Raw

    # misc.
    def compareTimeSeries(self, ts):
        """ Compares another time-series with itself to determine if both are identical 
            Four checks are performed:
                1. Label
                2. Parameters
                3. Raw BOLD associated with it
                4. Mask-file
            If all the three comparisions return true, then both the HRF
                time-series objects are identical
        """
        if self.label == ts.get_label() \
            and self.parameters == ts.get_parameters() \
            and self.BOLD_Raw.compareTimeSeries(ts.get_BOLD_Raw()) \
            and ts.get_maskfile() == self.mask_file:
            return True 
        else:
            return False 
            
    def save_info(self, name):
        """ Saves the information about the time-series in a .mat file """
        try:
            dic = {}
            dic["timeseries"] = self.timeseries
            dic["mask_file"] = self.mask_file 
            savemat(name, dic)
            return True
        except:
            return False