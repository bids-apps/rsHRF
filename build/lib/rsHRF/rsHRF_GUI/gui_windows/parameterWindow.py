from copy import deepcopy
from tkinter import Toplevel, Button, Entry, Label, DISABLED

class ParameterWindow():
    def __init__(self):
        self.window = Toplevel()
        self.window.title("Parameters")
        self.parameters = {}
        self.labels     = []
        self.entries    = []
        # get screen width and height
        screen_width  = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        self.window.geometry("350x420+%d+%d" % (screen_width*(280.0/1900), (((1040.0-220)/1000)*screen_height)-390))
        
    def updateParameters(self):
        for i in range(len(self.labels)):
            self.parameters[self.labels[i].cget('text')] = self.entries[i].get()
        parameters = dict(self.parameters)
        return deepcopy(parameters)

    def getParameters(self):
        return deepcopy(self.parameters)
    
    def setParameters(self, dic):
        self.parameters = deepcopy(dic) 
    
    def display(self): 
        # removing existing widgets
        for each in self.labels:
            each.destroy()
        for each in self.entries:
            each.destroy()
        # making new widgets
        self.labels  = []
        self.entries = []
        for each in self.parameters.keys():
            self.labels.append(Label(self.window, text=each))
            self.entries.append(Entry(self.window, width=15))
            if each == "passband" or each == "passband_deconvolve":
                self.entries[-1].insert(0, str(self.parameters[each][0]) + "," + str(self.parameters[each][1]))
            else:
                self.entries[-1].insert(0, str(self.parameters[each]))
            if each == "lag" or each == "dt":
                self.entries[-1].configure(state=DISABLED)
        row_i = 0
        while row_i < len(self.labels):
            key = self.labels[row_i].cget("text")
            if key == "estimation" or key == "temporal_mask":
                row_i += 1
                continue
            self.labels[row_i].grid(row=row_i,column=0,padx=(5,5),pady=(5,5))
            self.entries[row_i].grid(row=row_i,column=1,padx=(5,5),pady=(5,5))
            row_i += 1
