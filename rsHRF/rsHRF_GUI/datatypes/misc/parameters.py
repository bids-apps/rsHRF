import sys
import numpy as np
from copy           import deepcopy
from ...misc.status import Status

class Parameters():
    """ 
    rsHRF-Toolbox Parameters
    For more information, visit https://github.com/BIDS-Apps/rsHRF/tree/master/rsHRF
    """
    def __init__(self):
        # initialize default parameters
        self.estimation          = 'canon2dd'
        self.passband            = [0.01, 0.08]
        self.passband_deconvolve = [0.0, sys.float_info.max]
        self.TR                  = 2.0 
        self.localK              = 1
        self.T                   = 3
        self.T0                  = 1
        self.TD_DD               = 2
        self.AR_lag              = 1
        self.thr                 = 1
        self.order               = 3
        self.volterra            = 0
        self.len                 = 24      
        self.temporal_mask       = []
        self.min_onset_search    = 4
        self.max_onset_search    = 8
        self.dt                  = self.TR/self.T
        self.lag                 = np.arange(np.fix(self.min_onset_search / self.dt),
                                   np.fix(self.max_onset_search / self.dt) + 1,
                                   dtype='int')

    # getters
    def get_estimation(self):
        return self.estimation 
    
    def get_passband(self):
        return deepcopy(self.passband)

    def get_passband_deconvolve(self):
        return deepcopy(self.passband_deconvolve)
    
    def get_TR(self):
        return self.TR
    
    def get_localK(self):
        return self.localK
    
    def get_T(self):
        return self.T 
    
    def get_T0(self):
        return self.get_T0
    
    def get_TD_DD(self):
        # TD_DD is only relevant for canon2dd estimation
        if self.estimation == 'canon2dd':
            return self.TD_DD 
        else:
            return None 
    
    def get_AR_lag(self):
        return self.get_AR_lag 
    
    def get_thr(self):
        return self.thr 
    
    def get_order(self):
        # order is only relevant for fourier and gamma estimation
        if 'gamma' in self.get_estimation or 'fourier' in self.get_estimation:
            return self.order 
        else:
            return None 
    
    def get_Volterra(self):
        # volterra is only relevant for canon2dd estimation
        if self.get_estimation == 'canon2dd':
            return self.volterra
        else:
            return None 
    
    def get_len(self):
        return self.len 
    
    def get_temporal_mask(self):
        return tuple(self.temporal_mask)
    
    def get_min_onset_search(self):
        return self.min_onset_search
    
    def get_max_onset_search(self):
        return self.max_onset_search
    
    # setters
    def set_estimation(self,s):
        self.estimation = s
        return Status(True)
    
    def set_passband(self, l):
        """ 
        Takes a list (with two entries) as input and sets the 
            passband-range
        Checks whether both the values are non-negative 
        """
        try:
            l = [float(i) for i in l.split(",")]
            if l[0] < 0 or l[1] < 0:
                return Status(False, error="Passband frequency values cannot be negative")
        except:
            return Status(False, error="Bad datatype for passband range")
        else:
                self.passband = deepcopy(l)
                return Status(True)
    
    def set_passband_deconvolve(self, l):
        """ 
        Takes a list (with two entries) as input and sets the 
            passband-range
        Checks whether both the values are non-negative 
        """
        try:
            l = [float(i) for i in l.split(",")]
            if l[0] < 0 or l[1] < 0:
                return Status(False, error="Passband frequency values cannot be negative")
        except:
            return Status(False, error="Bad datatype for passband range")
        else:
                self.passband_deconvolve = deepcopy(l)
                return Status(True)
    
    def set_TR(self, TR):
        """ 
        Checks whether the value is postiive
        and updates 'dt' as it is dependent on TR
        """
        try:
            TR = float(TR)
        except:
            return Status(False,error="Bad Datatype For TR")
        else:
            if TR <= 0:
                return Status(False, error="BOLD Repetition Time must be greater than 0")
            else:
                self.TR = TR
                self.update_dt()
                return Status(True)
    
    def set_localK(self, localK):
        """
        Checks whether the value of localK is positive
        """
        try:
            localK = int(localK)
        except:
            return Status(False,error="Bad Datatype For localK")
        else:
            if localK <= 0:
                return Status(False, error="localK must be greater than 0")
            else:
                self.localK = localK
                return Status(True)
    
    def set_T(self, T):
        """
        Checks whether the value of T >= 1
        and updates 'dt' as it is dependent on T
        """
        try:
            T = int(T)
        except:
            return Status(False, error="Bad Datatype For T")
        else:
            if T < 1:
                return Status(False, error="Magnification factor must not be less than 1") 
            else:
                self.T = T 
                self.update_dt()
                return Status(True)
    
    def set_T0(self, T0):
        try:
            T0 = int(T0)
        except:
            return Status(False, error="Bad Datatype For T0")
        else:
            self.T0 = T0 
            return Status(True)
    
    def set_TD_DD(self, TD_DD):
        """
        Sets the value of TD_DD if the estimation is canon2dd
        """
        if self.estimation == 'canon':
            try:
                TD_DD = int(TD_DD)
            except:
                return Status(False, error="Magnification factor must not be less than 1") 
            if TD_DD not in [0,1,2]:
                return Status(False,error="TD_DD can only take one of these values: 0, 1, 2")
            else:
                self.TD_DD = TD_DD 
                return Status(True)
        else:
            return Status(True)
    
    def set_AR_lag(self, AR_lag):
        """
        Checks whether the AR_lag is non-negative
        """
        try:
            AR_lag = int(AR_lag)
        except:
            return Status(False, error="Bad datatype for AR_lag")
        else:
            if AR_lag < 0:
                return Status(False, error="AR_lag must not be negative")
            else:
                self.AR_lag = AR_lag 
                return Status(True)
    
    def set_thr(self, thr):
        """
        If estimation is FIR or sFIR, thr is a list
        Otherwise, it is an int
        """
        if 'FIR' not in self.estimation :
            try:
                thr = int(thr)
            except:
                return Status(False, error="Bad datatype for thr")
            else:
                self.thr = thr 
                return Status(True)
        else:
            try:
                thr = [int(i) for i in thr.split(",")]
            except:
                return Status(False, error="Bad datatype for thr")
            else:
                self.thr = thr 
                return Status(True)
    
    def set_order(self, order):
        """
        Checks whether the order lies between 1 to 60
        """
        try:
            order = int(order)
        except:
            return Status(False, error="Bad datatype for order")
        else:
            if order < 0 or order > 60:
                status = Status(False)
                if order < 0:
                    status.set_error("Order must not be negative")
                elif order > 60:
                    status.set_error("Order is too high")
                return status
            else:
                self.order = order 
                return Status(True)
    
    def set_Volterra(self, volterra):
        """
        Sets Volterra if the estimation rule is canon2dd
        """
        if self.estimation == 'canon':
            try:
                volterra = int(volterra)
            except:
                return Status(False, error="Bad datatype for Volterra")
            else:
                self.volterra = volterra
                return Status(True)
        else:
            return Status(True)
    
    def set_len(self, length):
        """
        Checks whether the length of the hemodynamic response function is non-negative
        """
        try:
            length = int(length)
        except:
            return Status(False, error="Bad datatype for len")
        else:
            if length <= 0:
                status = Status(False)
                status.set_error("HRF length must not be postitive")
                return status
            else:
                self.len = length 
                return Status(True)
    
    def set_temporal_mask(self, temporal_mask):
        self.temporal_mask = deepcopy(temporal_mask)
        return Status(True)
    
    def set_min_onset_search(self, mos):
        """
        Checks whether the min-onset-search is smaller than max-onset-search
        and non-negative
        """
        try:
            mos = int(mos)
        except:
            return Status(False, error="Bad datatype for min_onset_search")
        else:
            if mos > self.max_onset_search or mos < 0:
                status = Status(False)
                if mos > self.max_onset_search:
                    status.set_error("Min Onset Search must not be greater than Max Onset Search")
                elif mos < 0:
                    status.set_error("Onset Search values must not be negative")
                return status 
            else:
                self.min_onset_search = mos
                self.update_lag()
                return Status(True) 
    
    def set_max_onset_search(self, mos):
        """
        Checks whether max-onset-search is greater than min-onset-search
        and non-negative
        """
        try:
            mos = int(mos)
        except:
            return Status(False, error="Bad datatype for max_onset_search")
        else:
            if mos < self.min_onset_search or mos < 0:
                status = Status(False)
                if mos < self.min_onset_search:
                    status.set_error("Max Onset Search must not be lesser than Min Onset Search")
                elif mos < 0:
                    status.set_error("Onset Search values must not be negative")
                return status 
            else:
                self.max_onset_search = mos
                self.update_lag()
                return Status(True)

    def update_dt(self):
        """
        Re-calculating dt
        """
        self.dt  = self.TR / self.T 
        self.update_lag()
    
    def update_lag(self):
        """
        Re-calculating lag
        """
        self.lag = np.arange(np.fix(self.min_onset_search / self.dt),
                    np.fix(self.max_onset_search / self.dt) + 1,
                    dtype='int')
    
    def get_parameters(self):
        """
        Gets all the parameters in the form of a dictionary for rsHRF computation
        """
        para                            = {}
        para['estimation']              = self.estimation
        para['passband']                = deepcopy(self.passband)
        para['passband_deconvolve']     = deepcopy(self.passband_deconvolve)
        para['TR']                      = self.TR
        para['T']                       = self.T 
        para['localK']                  = self.localK
        para['T0']                      = self.T0
        para['AR_lag']                  = self.AR_lag
        para['thr']                     = self.thr
        para['len']                     = self.len
        para['temporal_mask']           = deepcopy(self.temporal_mask)
        para['min_onset_search']        = self.min_onset_search
        para['max_onset_search']        = self.max_onset_search
        if self.estimation == 'canon2dd':
            para['TD_DD']               = self.TD_DD
            para['Volterra']            = self.volterra
        elif 'gamma' in self.estimation or 'fourier' in self.estimation:
            para['order']               = self.order 
        para['dt']                      = self.dt 
        para['lag']                     = self.lag 
        return para
        
    def set_parameters(self, dic):
        """
        Takes a dictionary as input and sets all the rsHRF parameters accordingly
        """
        for key in dic.keys():
            if key   == "estimation":
                out  = self.set_estimation(dic[key])
            elif key == "passband":
                out  = self.set_passband(dic[key])
            elif key == "passband_deconvolve":
                out  = self.set_passband_deconvolve(dic[key])
            elif key == "T":
                out  = self.set_T(dic[key])
            elif key == "TR":
                out  = self.set_TR(dic[key])
            elif key == "localK":
                out  = self.set_localK(dic[key])
            elif key == "T0":
                out  = self.set_T0(dic[key])
            elif key == "TD_DD":
                out  = self.set_TD_DD(dic[key])
            elif key == "AR_lag":
                out  = self.set_AR_lag(dic[key])
            elif key == "thr":
                out  = self.set_thr(dic[key])
            elif key == "order":
                out  = self.set_order(dic[key])
            elif key == "Volterra":
                out  = self.set_thr(dic[key])
            elif key == "len":
                out  = self.set_len(dic[key])
            elif key == "temporal_mask":
                out  = self.set_temporal_mask(dic[key])
            elif key == "min_onset_search":
                out  = self.set_min_onset_search(dic[key])
            elif key == "max_onset_search":
                out  = self.set_max_onset_search(dic[key])
            if not out.get_state():
                return out 
        return Status(True, info="Parameters Updated Succefully")
            
    def compareParameters(self, p):
        """
        Takes another parameter object and determines if it is equal 
        to the this object
        """
        x = self.get_parameters()
        y = p.get_parameters()
        for key in x.keys():
            if key not in y.keys():
                return False 
            elif key == "dt" or key == "lag":
                continue 
            else:
                if x[key] != y[key]:
                    return False 
        return True
