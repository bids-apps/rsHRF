from .plotterWindow import PlotterWindow
from tkinter import Toplevel, OptionMenu, StringVar, _setit, Entry, IntVar, Checkbutton

class PlotterOptionsWindow():
    def __init__(self):
        window = Toplevel()
        window.title("Plotting Menu")
        # get screen width and height
        screen_width  = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window.geometry("650x200+%d+%d" % (screen_width/2.95, 100 + screen_height/2))
        self.plotterScreen = PlotterWindow()
        
        # can have 3 different plots at once
        self.numberOfPlots = self.plotterScreen.get_numberOfPlots()
        self.plot          = [StringVar() for i in range(self.numberOfPlots)]
        self.plotVal       = [IntVar() for i in range(self.numberOfPlots)]
        self.plotValStore  = [0 for i in range(self.numberOfPlots)]
        self.plotables     = []
        self.options       = ["None"]
        for each in self.plot:
            each.set("None")

        def plotTS():
            for i in range(0, self.numberOfPlots):
                if self.plotVal[i].get() != self.plotValStore[i]:
                    self.plotValStore[i]  = self.plotVal[i].get()
                    if self.plotValStore[i] == 0:
                        self.plotterScreen.makePlot(None, 0, i)
                        return
                    for each in self.plotables:
                        if each[0] == self.plot[i].get():
                            self.plotterScreen.makePlot(each[1][:,int(self.selectVoxel[i].get())], 1, i)
                            return 
                    self.plotterScreen.makePlot(None, 0, i)
                    return   
                
        self.plotSelectDropDown = [OptionMenu(window, self.plot[i], *self.options) for i in range(self.numberOfPlots) for i in range(self.numberOfPlots)]
        self.selectVoxel        = [Entry(window, width=10) for i in range(self.numberOfPlots) for i in range(self.numberOfPlots)]
        self.plotButton         = [Checkbutton(window, text=" Plot TS " + str(i), variable=self.plotVal[i], command=plotTS) for i in range(self.numberOfPlots)]

        for each in self.selectVoxel:
            each.insert(0, 0)

        for i in range(0, self.numberOfPlots):
            self.plotSelectDropDown[i].grid(row=0,column=i,padx=(5,5),pady=(5,5))
            self.selectVoxel[i].grid       (row=1,column=i,padx=(5,5),pady=(5,5))
            self.plotButton[i].grid        (row=2,column=i,padx=(5,5),pady=(5,5))

    def updatePlots(self, plotables):
        temp_names = []
        for each in self.plotables:
            temp_names.append(each[0])
        for each in plotables:
            if each[0] not in temp_names:
                self.plotables.append(each)
        self.options = ["None"]
        for each in self.plotables:
            self.options.append(each[0])
        self.options[1:] = sorted(self.options[1:])
        self.updateWidgets()

    def updateWidgets(self):

        if len(self.options) == 0:
            self.options.append("None")

        for each in self.plotSelectDropDown:
            each['menu'].delete(0, 'end')

        for choice in self.options:
            for i in range(0, self.numberOfPlots):
                self.plotSelectDropDown[i]['menu'].add_command(label=choice, command=_setit(self.plot[i], choice))

    def get_plotables(self):
        return self.plotables
