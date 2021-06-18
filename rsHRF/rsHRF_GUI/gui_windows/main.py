import os
import time
from scipy.io   import savemat
from tkinter    import Tk, Button, Label, OptionMenu, StringVar

from .inputWindow          import InputWindow
from .loggingWindow        import LoggingWindow
from .plotterOptionsWindow import PlotterOptionsWindow
from .parameterWindow      import ParameterWindow
     
from ..misc.status import Status
from ..core.core   import Core 

class Main():
    def __init__(self):
        # main window
        root = Tk()
        root.title("rsHRF Toolbox")
        # get screen width and height
        screen_width     = root.winfo_screenwidth()
        screen_height    = root.winfo_screenheight()
        # placing the toplevel
        root.geometry("500x300+%d+%d" % (((280/1900)*screen_width + 425), (((1040.0-220)/1000)*screen_height)-670))
        # defining the toplevels
        input_window     = InputWindow()
        parameter_window = ParameterWindow()
        core             = Core()
        logger           = LoggingWindow()
        plotter          = PlotterOptionsWindow()
        # defining variables used by tkinter widgets
        current          = StringVar()
        current_subject  = StringVar()
        output_path      = os.getcwd()
        self.options     = ["None"]
        self.subjects    = ["None"]
        current.set        ("None")
        current_subject.set("None")
        # other variables
        input            = ()    # receives the input from the input window
        output           = {}    # receives the output from the core 
        # initializing parameter window
        parameter_window.setParameters(core.get_parameters())
        parameter_window.display()

        ''' Gets the input from the input toplevel.
            The input comprises of three elements:
                1. Input file (resting-state fMRI)
                2. Brain Mask
                3. Estimation Rule
        '''
        def makeInput():
            start                    = time.process_time()
            # interacting with the input window
            input                    = input_window.getInput()
            # interacting with the back-end
            parameters               = parameter_window.getParameters()
            parameters['estimation'] = input[-2]
            core.updateParameters(parameters)      # only passing the estimation-rule
            output                   = core.makeInput(input[:-2])  # receiving input from core
            output_path              = input[-1]                      # the path to output directory
            # interacting with the parameter-window
            parameter_window.setParameters(core.get_parameters())
            parameter_window.display()
            # updating data
            updateSubjects()
            # logging
            time_taken                  = time.process_time() - start
            output.set_time(str(time_taken)[:5])
            logger.putLog(status=output)

        def changeEstimationRule():
            start = time.process_time()
            # interacting with the input window
            input                       = input_window.getInput()
            # interacting with the core
            output                      = core.updateParameters({"estimation":input[-2]})
            # interacting with the parameter-window
            parameter_window.setParameters(core.get_parameters())
            parameter_window.display()
            # logging
            time_taken                  = time.process_time() - start
            output.set_time(str(time_taken)[:5])
            logger.putLog(status=output)

        def updateParameters():
            start                       = time.process_time()
            # interacting with the core
            output                      = core.updateParameters(dic=parameter_window.updateParameters())
            # interacting with the parameter-window
            parameter_window.setParameters(core.get_parameters())
            parameter_window.display()
            time_taken                  = time.process_time() - start
            # logging
            output.set_time(str(time_taken)[:5])
            logger.putLog(status=output)
        
        def retrieveHRF(get_pos=False):
            if "Preprocessed-BOLD" not in current.get():
                logger.putLog(status=Status(False, error="Select a Preprocessed-BOLD Timeseries to retrieve HRF"))
            else:
                start                       = time.process_time()
                core.updateParameters(dic   =parameter_window.updateParameters())
                bold_ts                     = core.get_time_series(current.get())
                output                      = core.retrieveHRF(bold_ts, get_pos)
                # updating data
                updateValues(log=False)
                # logging
                time_taken                  = time.process_time() - start
                if get_pos:
                    output, pos = output 
                else:
                    pos         = None
                output.set_time(str(time_taken)[:5])
                logger.putLog(status=output)
                return pos

        def retrieveHRFParameters(pos=None):
            if pos != None:
                current.set(current.get().split("_")[0] + "_HRF_" + str(pos))
            if "HRF" not in current.get():
                logger.putLog(status=Status(False, error="Select an HRF Timeseries to retrieve parameters"))
            else:
                start                       = time.process_time()
                # interacting with the core
                output                      = core.getHRFParameters(core.get_time_series(current.get()))
                # updating data
                updateValues(log=False)
                # logging
                time_taken                  = time.process_time() - start 
                output.set_time(str(time_taken)[:5])
                logger.putLog(status=output)

        def deconvolveHRF(pos=None):
            if pos != None:
                current.set(current.get().split("_")[0] + "_HRF_" + str(pos))
            if "HRF" not in current.get():
                logger.putLog(status=Status(False, error="Select an HRF Timeseries to deconvolve BOLD"))
            else:
                start                       = time.process_time()
                # interacting with the core
                output                      = core.deconvolveHRF(core.get_time_series(current.get()))
                # updating data
                updateValues(log=False)
                # logging
                time_taken                  = time.process_time() - start 
                output.set_time(str(time_taken)[:5])
                logger.putLog(status=output)

        def runCompletePipeline():
            if "Preprocessed-BOLD" in current.get():
                pos = retrieveHRF(get_pos=True)
                retrieveHRFParameters(pos)
                deconvolveHRF(pos)
            elif "HRF" in current.get():
                retrieveHRFParameters()
                deconvolveHRF()
            else:
                logger.putLog(status=Status(False, error="Select an HRF or Preprocessed-BOLD Timeseries to run pipeline"))

        def updatePlots():
            # interacting with the core
            try:
                plotables                   = core.get_plotables(current_subject.get())
            except: 
                logger.putLog(status=Status(False, error="Please select a subject"))
            else:
                # logging
                if plotables == None:
                    logger.putLog(status=Status(False, error="Please select a subject"))
                else:
                    logger.putLog(plotables=plotables)
                    # interacting with the plotter
                    plotter.updatePlots(plotables)

        def getInfo():
            try:
                if len(current.get().split("_")) == 3:
                    logger.putLog(data_info=core.get_store_info(current.get()))
                else:
                    logger.putLog(status = Status(False, error="Select a valid input to get information")) 
            except: 
                logger.putLog(status = Status(False, error="Select a valid input to get information")) 
   
        def saveValue():
            try:
                if len(current.get().split("_")) == 3:
                    if os.path.isdir(output_path):
                        out = output_path 
                    else:
                        out = os.cwd() 
                    if core.save_info(current.get(), out):
                        logger.putLog(status = Status(True, info="File saved successfully"))   
                    else:
                        logger.putLog(status = Status(False, error="Unable to save file"))      
                else:
                    logger.putLog(status = Status(False, error="Select a valid input to save")) 
            except:
                logger.putLog(status = Status(False, error="Select a valid input to save")) 

        def saveForSubject():
            try:
                temp                        = core.get_data_labels(current_subject.get())
            except:
                logger.putLog(status=Status(False, error="Please select a subject")) 
            else:
                for each in temp:
                    current.set(each)
                    saveValue()
        
        def add_new(l1, l2):
            if l1 == None:
                return l2 
            if l2 == None:
                return l1
            out = []
            for each in l1:
                if each not in l2:
                    out.append(each)
            for each in l2:
                out.append(each)
            return out
        
        def updateSubjects():
            temp                        = list(core.get_subjects())
            temp.append                 ("None")
            self.subjects               = add_new(self.subjects, temp)
            self.subjects               = sorted(self.subjects)
            subjectOptions              = OptionMenu(root, current_subject, *self.subjects)
            subjectOptions.grid         (row=0,column=1,padx=(30,30),pady=(5,5))
        
        def updateValues(log=True):
            try:
                temp                        = core.get_data_labels(current_subject.get())
            except:
                logger.putLog(status=Status(False, error="Please select a subject"))
            else:
                if log:
                    logger.putLog(status=Status(True, info="Updated values for subject: " + current_subject.get()))
                temp.append             ("None")
                self.options            = add_new(self.options, temp)
                self.options            = sorted(self.options)
                valueOptions            = OptionMenu(root, current,         *self.options)
                valueOptions.grid       (row=1,column=1,padx=(30,30),pady=(5,5))

       

        # defining the widgets
        getInput                        = Button    (root, text="Get Input",               command=makeInput,             height = 1, width = 20)
        changeParameterButton           = Button    (root, text="Update Parameters",       command=updateParameters,      height = 1, width = 20)
        retrieveHRFButton               = Button    (root, text="Retrieve HRF",            command=retrieveHRF,           height = 1, width = 20)
        retrieveHRFParametersButton     = Button    (root, text="Retrieve HRF Parameters", command=retrieveHRFParameters, height = 1, width = 20)
        deconvolveHRFButton             = Button    (root, text="Deconvolve BOLD",         command=deconvolveHRF,         height = 1, width = 20)
        updatePlotsButton               = Button    (root, text="Update Plots",            command=updatePlots,           height = 1, width = 20)
        changeEstimationRule            = Button    (root, text="Set Estimation Rule",     command=changeEstimationRule,  height = 1, width = 20)
        getValueInfo                    = Button    (root, text="Get Info",                command=getInfo,               height = 1, width = 20)
        storeValue                      = Button    (root, text="Save Value",              command=saveValue,             height = 1, width = 20)
        updateStore                     = Button    (root, text="Update Values",           command=updateValues,          height = 1, width = 20)
        runCompletePipeline             = Button    (root, text="Run Pipeline",            command=runCompletePipeline,   height = 1, width = 20)
        saveAllValues                   = Button    (root, text="Save All",                command=saveForSubject,        height = 1, width = 20)
        dataLabel                       = Label     (root, text="Stored Values: ")
        subjectLabel                    = Label     (root, text="Subjects: ")
        valueOptions                    = OptionMenu(root, current,         *self.options)
        subjectOptions                  = OptionMenu(root, current_subject, *self.subjects)
        # placing the widgets
        subjectLabel.grid               (row=0,column=0,padx=(30,30),pady=(5,5))
        subjectOptions.grid             (row=0,column=1,padx=(30,30),pady=(5,5))
        dataLabel.grid                  (row=1,column=0,padx=(30,30),pady=(5,5))
        valueOptions.grid               (row=1,column=1,padx=(30,30),pady=(5,5))
        getInput.grid                   (row=2,column=0,padx=(30,30),pady=(5,5))
        updateStore.grid                (row=2,column=1,padx=(30,30),pady=(5,5))
        changeEstimationRule.grid       (row=3,column=0,padx=(30,30),pady=(5,5))
        changeParameterButton.grid      (row=3,column=1,padx=(30,30),pady=(5,5))
        retrieveHRFButton.grid          (row=4,column=0,padx=(30,30),pady=(5,5))
        retrieveHRFParametersButton.grid(row=4,column=1,padx=(30,30),pady=(5,5))
        deconvolveHRFButton.grid        (row=5,column=0,padx=(30,30),pady=(5,5))
        updatePlotsButton.grid          (row=5,column=1,padx=(30,30),pady=(5,5))
        getValueInfo.grid               (row=6,column=0,padx=(30,30),pady=(5,5))
        storeValue.grid                 (row=6,column=1,padx=(30,30),pady=(5,5))
        runCompletePipeline.grid        (row=7,column=0,padx=(30,30),pady=(5,5))
        saveAllValues.grid              (row=7,column=1,padx=(30,30),pady=(5,5))

        root.mainloop()
    

if __name__ == "__main__":
    Main()