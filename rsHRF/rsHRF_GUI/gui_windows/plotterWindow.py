import mpld3
import matplotlib
matplotlib.use("TkAgg")
import numpy as np
from matplotlib.figure                 import Figure
from tkinter                           import ttk, Toplevel, Canvas, TOP, BOTH, BOTTOM
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class PlotterWindow():  
    def __init__(self):
        window = Toplevel()
        window.title("Screen")
        # get screen width and height
        screen_width       = window.winfo_screenwidth()
        screen_height      = window.winfo_screenheight()
        window.geometry("600x400+%d+%d" % (screen_width-600, screen_height/2))
        figure             = Figure(figsize=(5,5), dpi=100)
        self.numberOfPlots = 3
        self.ts            = [[] for i in range(0, self.numberOfPlots)]
        self.plot          = [figure.add_subplot(111) for i in range(0, self.numberOfPlots)]
        self.canvas        = FigureCanvasTkAgg(figure, window)

    def get_numberOfPlots(self):
        return self.numberOfPlots

    def makePlot(self, ts, val, num):
        for each in self.plot:
            each.clear()
        if val == 0:
            self.ts[num] = 0
        elif val == 1:
            self.ts[num] = ts
        for i in range(self.numberOfPlots):
            self.plot[i].plot(self.ts[i])
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

