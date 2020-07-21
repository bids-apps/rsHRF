from . import subject
class Store():
    def __init__(self):
        self.subjects = []

    # getters
    def get_subjects(self):
        return tuple(self.subjects) 
    
    def get_subject_by_index(self, index):
        for each in self.subjects:
            if each.get_subject_index() == index:
                return each
    
    def get_subject(self, input_filename, mask_filename):
        for each in self.subjects:
            if each.get_input_filename() == input_filename and each.get_mask_filename() == mask_filename:
                return each 
    
    def get_plotables(self, index):
        for each in self.subjects:
            if each.get_subject_index() == index:
                return each.get_plotables()
    
    def get_data_labels(self, index):
        for each in self.subjects:
            if each.get_subject_index() == index:
                return each.get_data()
    
    def get_time_series(self, s):
        s = s.split("_")
        index = s[0]
        ts_type = s[1]
        ts_num = int(s[2])
        for each in self.subjects:
            if each.get_subject_index() == index:
                return each.get_time_series_by_index(ts_type, ts_num)
        return 
    
    def get_info(self, s):
        ts = self.get_time_series(s)
        subject_index = ts.get_subject_index()
        subject = self.get_subject_by_index(subject_index)
        dic = ts.get_info()
        if ts.get_label() == "HRF":
            dic["Associated BOLD"] = subject_index + "_BOLD_" + subject.get_time_series(ts.get_associated_BOLD(), pos=True)
        elif ts.get_label() == "Deconvolved-BOLD":
            dic["Associated HRF"] = subject_index + "_HRF_" + subject.get_time_series(ts.get_associated_HRF(), pos=True)
        return dic
    
    # misc.
    def update_subject(self, subject):
        for i in range(0, len(self.subjects)):
            if self.subjects[i].get_input_filename() == subject.get_input_filename() and self.subjects[i].get_mask_filename() == subject.get_mask_filename():
                self.subjects[i] = subject
    
    def add_subject(self, sub):
        self.subjects.append(sub)
    
    def remove_subject(self, sub):
        new_subjects = []
        for each in self.subjects:
            if each.get_subject_index() == sub.get_subject_index():
                continue 
            else:
                new_subjects.append(each)
        self.subjects = new_subjects
    
    def number_of_subjects(self):
        return len(self.subjects)
    
    def save_info(self, s, out):
        ts = self.get_time_series(s)
        return ts.save_info(out+"/sub-"+s+".mat")