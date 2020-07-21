import numpy as np
from copy import deepcopy

class Subject():
    def __init__(self, input_filename, mask_filename=""):
        self.input_filename = input_filename 
        self.mask_filename  = mask_filename
        self.index          = self.input_filename.split("/")[-1].split("_")[0][4:]
        self.BOLD           = []
        self.BOLD_pre       = []
        self.BOLD_deconv    = []
        self.HRF            = []
    
    # setter
    def set_mask_filename(self, mask_filename):
        self.mask_filename = mask_filename

    # getters
    def get_input_filename(self):
        return self.input_filename 

    def get_mask_filename(self):
        return self.mask_filename 
    
    def get_subject_index(self):
        return self.index
    
    def get_BOLD(self):
        return tuple(self.BOLD)
    
    def get_BOLD_pre(self):
        return tuple(self.BOLD_pre)
    
    def get_BOLD_deconv(self):
        return tuple(self.BOLD_deconv)
    
    def get_HRF(self):
        return tuple(self.HRF)
    
    def get_time_series(self, ts, pos=False):
        label = ts.get_label()
        if label == "BOLD":
            arr = self.BOLD 
        elif label == "Preprocessed-BOLD":
            arr = self.BOLD_pre 
        elif label == "Deconvolved-BOLD":
            arr = self.BOLD_deconv
        elif label == "HRF":
            arr = self.HRF 
        else :
            arr = []
        i = 0
        for each in arr:
            i += 1
            if ts.compareTimeSeries(each):
                if pos:
                    return str(i-1) 
                else:
                    return each
        return None

    def get_time_series_by_index(self, ts_type, index):
        if ts_type == "BOLD":
            arr = self.BOLD 
        elif ts_type == "Preprocessed-BOLD":
            arr = self.BOLD_pre 
        elif ts_type == "Deconvolved-BOLD":
            arr = self.BOLD_deconv 
        elif ts_type == "HRF":
            arr = self.HRF 
        else:
            return
        return arr[index]

    def get_plotables(self):
        out = []
        i = 0
        while i < len(self.BOLD):
            out.append((self.index+"_BOLD_"+str(i),self.BOLD[i].get_ts()))
            i += 1
        i = 0
        while i < len(self.BOLD_pre):
            out.append((self.index+"_Preprocessed-BOLD_"+str(i),self.BOLD_pre[i].get_ts()))
            i += 1
        i = 0
        while i < len(self.BOLD_deconv):
            out.append((self.index+"_Deconvolved-BOLD_"+str(i),self.BOLD_deconv[i].get_ts()))
            i += 1
        i = 0
        while i < len(self.HRF):
            out.append((self.index+"_HRF_"+str(i),self.HRF[i].get_ts()))
            i += 1
        return out

    def get_data(self):
        out = []
        i = 0
        while i < len(self.BOLD):
            out.append(self.index+"_BOLD_"+str(i))
            i += 1
        i = 0
        while i < len(self.BOLD_pre):
            out.append(self.index+"_Preprocessed-BOLD_"+str(i))
            i += 1
        i = 0
        while i < len(self.BOLD_deconv):
            out.append(self.index+"_Deconvolved-BOLD_"+str(i))
            i += 1
        i = 0
        while i < len(self.HRF):
            out.append(self.index+"_HRF_"+str(i))
            i += 1
        return out

    # adding to time-series objects of the existing subject
    def add_BOLD(self, ts):
        self.BOLD.append(deepcopy(ts)) 
    def add_BOLD_deconv(self, ts):
        self.BOLD_deconv.append(deepcopy(ts))
    def add_BOLD_pre(self, ts):
        self.BOLD_pre.append(deepcopy(ts))
    def add_HRF(self, ts):
        self.HRF.append(deepcopy(ts))
    
    
