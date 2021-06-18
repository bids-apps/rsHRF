from . import subject

class Store():
    """
    Stores all the subjects as a dictionary, with their keys as the index
    """
    def __init__(self):
        self.subjects = {}

    # getters
    def get_subjects(self):
        """ Returns a tuple with the indices of all subjects"""
        return tuple(self.subjects.keys()) 
    
    def get_subject_by_index(self, index):
        """ Takes subject-index as the input and returns the corresponding subject """
        try:
            return self.subjects[index]
        except:
            return None
    
    def get_plotables(self, index):
        """ Gets all the time-series that can be plotted, for a particular subject"""
        return self.subjects[index].get_plotables()
    
    def get_data_labels(self, index):
        """ Gets the labels for all the time-series data for that subject"""
        return self.subjects[index].get_data_labels()
    
    # misc.
    def get_time_series(self, s):
        """ Gets the time-series object corresponding to s"""
        s       = s.split("_")
        index   = s[0]
        ts_type = s[1]
        ts_num  = int(s[2])
        return self.subjects[index].get_time_series_by_index(ts_type, ts_num)
    
    def get_info(self, s):
        """ Gets all the information about a time-series to be displayed to the logging-window """
        ts            = self.get_time_series(s)
        subject_index = ts.get_subject_index()
        subject       = self.subjects[subject_index]
        dic           = ts.get_info()
        if ts.get_label()   == "BOLD":
            dic["Input File"]          = ts.get_inputfile()
        elif ts.get_label() == "Preprocessed-BOLD":
            dic["Mask File"]           = ts.get_maskfile()
            dic["Associated Raw BOLD"] = subject_index + "_BOLD_"               + subject.get_time_series_pos(ts.get_BOLD_Raw())
        elif ts.get_label() == "HRF":
            dic["Associated BOLD"]     = subject_index + "_Preprocessed-BOLD_"  + subject.get_time_series_pos(ts.get_associated_BOLD())
        elif ts.get_label() == "Deconvolved-BOLD":            
            dic["Associated HRF"]      = subject_index + "_HRF_"                + subject.get_time_series_pos(ts.get_associated_HRF())
        return dic

    def is_present(self, subject_index):
        """ Checks whether a subject-index is present is already present"""
        if subject_index in self.subjects.keys():
            return True
        return False
    
    def add_subject(self, sub):
        """ Adds a new subject """
        self.subjects[sub.get_subject_index()] = sub
    
    def remove_subject(self, sub):
        """ Removing a subject """
        try:
            del self.subjects[sub.get_subject_index()]
        except:
            return 
    
    def number_of_subjects(self):
        """ Gets the number of subjects """
        return len(self.subjects.keys())
    
    def save_info(self, s, out):
        """ Saves all the time-series objects for a particular subject in the form of .mat files """
        ts = self.get_time_series(s)
        return ts.save_info(out+"/sub-"+s+".mat")