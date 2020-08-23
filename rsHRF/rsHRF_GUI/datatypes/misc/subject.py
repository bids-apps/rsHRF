import numpy as np

class Subject():
    """
    Stores the information corresponding to a particular subject.

    Attrbutes:
        1. index          : This is the index of the subject (as determined by BIDS convention)
        2. BOLD_raw       : An array which stores the corresponding Raw BOLD time-series for the subject
        3. BOLD_pre       : An array which stores the corresponding Preprocessed-BOLD time-series for the subject
        4. BOLD_deconv    : An array which stores the corresponding Deconvolved-BOLD time-series for the subject
        5. HRF            : An array which stores the corresponding Hemodynamic Response Function time-series for the subject

        -> All the attributes from 2-5, are arrays of TimeSeries objects
    """
    def __init__(self, index):
        self.index          = index
        self.BOLD_raw       = []
        self.BOLD_pre       = []
        self.BOLD_deconv    = []
        self.HRF            = []
    
    # getters
    def get_input_filename(self):
        return self.input_filename 
    
    def get_subject_index(self):
        return self.index
    
    def get_BOLD_raw(self):
        return tuple(self.BOLD_raw)
    
    def get_BOLD_pre(self):
        return tuple(self.BOLD_pre)
    
    def get_BOLD_deconv(self):
        return tuple(self.BOLD_deconv)
    
    def get_HRF(self):
        return tuple(self.HRF)

    # adding to time-series objects of the existing subject
    def add_BOLD_raw(self, ts):
        self.BOLD_raw.append(ts) 
        return len(self.BOLD_raw) - 1

    def add_BOLD_deconv(self, ts):
        self.BOLD_deconv.append(ts)
        return len(self.BOLD_raw) - 1

    def add_BOLD_pre(self, ts):
        self.BOLD_pre.append(ts)
        return len(self.BOLD_raw) - 1

    def add_HRF(self, ts):
        self.HRF.append(ts)
        return len(self.BOLD_raw) - 1

    # misc.
    def is_present(self, label, misc, getts=False):
        """ Checks whether a time-series is already present 
            Misc takes in all the relevant information which determines the uniqueness
                of a time-series
            If getts = True, the function returns the time-series object if it is present """
        if label == "BOLD":
            # Looking for Raw BOLD Data
            for each in self.BOLD_raw:
                # Determines whether the Raw BOLD data is already present
                # Checks for the input-file
                if misc == each.get_inputfile():
                    if getts :
                        return each
                    return True 
        elif label == "Preprocessed-BOLD":
            # Looking for Preprocessed BOLD Data
            para     = misc[0]
            mask     = misc[1]
            bold     = misc[2]
            for each in self.BOLD_pre:
                # Determines whether Preprocessed BOLD data is already present
                # Checks the parameters, mask-file and RAW Bold
                if para.compareParameters(each.get_parameters()) \
                    and each.get_maskfile() == misc[1] \
                    and bold.compareTimeSeries(each.get_BOLD_Raw()):
                    if getts:
                        return each
                    return True 
        elif label == "HRF":
            # Looking for HRF Data
            para     = misc[0]
            BOLD_pre = misc[1]
            for each in self.HRF:
                # Determines whether the HRF is already present
                # Checks the parameters and Preprocessed BOLD
                if para.compareParameters(each.get_parameters()) \
                    and BOLD_pre.compareTimeSeries(each.get_associated_BOLD()):
                    if getts:
                        return each
                    return True
        elif label == "Deconvolved-BOLD":
            # Looking for Deconvolved BOLD Data
            para = misc[0]
            HRF  = misc[1]
            for each in self.BOLD_deconv:
                # Determines whether the Deconvolved BOLD is already present
                # Checks the associated HRF
                if para.compareParameters(each.get_parameters()) \
                    and HRF.compareTimeSeries(each.get_associated_HRF()):
                    if getts :
                        return each
                    return True
        return False
    
    def get_time_series_pos(self, ts):
        """ 
        Takes the time-series as input and returns its position in the array
        """
        label = ts.get_label()
        if label    == "BOLD":
            arr     = self.BOLD_raw 
        elif label  == "Preprocessed-BOLD":
            arr     = self.BOLD_pre 
        elif label  == "Deconvolved-BOLD":
            arr     = self.BOLD_deconv
        elif label  == "HRF":
            arr     = self.HRF 
        else :
            arr     = []
        for i in range(len(arr)):
            if ts.compareTimeSeries(arr[i]):
                return str(i)
        return None

    def get_time_series_by_index(self, ts_type, index):
        """ Takes the index of a time-series and returns the time-series """
        if ts_type == "BOLD":
            arr = self.BOLD_raw 
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
        """ 
        Returns an array of all the time-series objects that can be plotted for the subject
        The array contains of tuples of the format : (time-series labels, time-series numpy arrays) 
        """
        out = []
        for i in range(len(self.BOLD_raw)):
            out.append((self.index+"_BOLD_"+str(i),self.BOLD_raw[i].get_ts()))
        for i in range(len(self.BOLD_pre)):
            out.append((self.index+"_Preprocessed-BOLD_"+str(i),self.BOLD_pre[i].get_ts()))
        for i in range(len(self.BOLD_deconv)):
            out.append((self.index+"_Deconvolved-BOLD_"+str(i),self.BOLD_deconv[i].get_ts()))
        for i in range(len(self.HRF)):
            out.append((self.index+"_HRF_"+str(i),self.HRF[i].get_ts()))
        return out

    def get_data_labels(self):
        """
        Returns an array with labels for all the time-series objects for the subject 
        """
        out = []
        for i in range(len(self.BOLD_raw)):
            out.append(self.index+"_BOLD_"+str(i))
        for i in range(len(self.BOLD_pre)):
            out.append(self.index+"_Preprocessed-BOLD_"+str(i))
        for i in range(len(self.BOLD_deconv)):
            out.append(self.index+"_Deconvolved-BOLD_"+str(i))
        for i in range(len(self.HRF)):
            out.append(self.index+"_HRF_"+str(i))
        return out

    
    
