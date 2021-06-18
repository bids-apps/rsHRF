import os
from tkinter       import Toplevel, Checkbutton, IntVar, Button, filedialog, NORMAL, DISABLED, OptionMenu, StringVar, Label


class InputWindow():
    def __init__(self):
        # input window
        window = Toplevel()
        window.title("Input Window")
        # get screen width and height
        screen_width  = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        # placing the toplevel
        window.geometry("350x220+%d+%d" % ((280/1900)*screen_width, ((((1040.0-220)/1000)*screen_height)-390)-280))
        # variables which shall get sent to the front end
        self.input_file = ()
        self.mask_file  = ()
        self.file_type  = ()
        self.output_dir = ()
        # other class vairables
        # 1 corresponds to BIDS input
        self.inputFormatVar = IntVar()
        self.inputFormatVar.set(0) 
        # 1 corresponds to mask file being present in the BIDS directory
        self.maskFormatVar = IntVar()
        self.maskFormatVar.set(0) 
        # selecting the estimation rule
        self.estimationOption = StringVar()
        self.estimationOption.set('canon2dd')

        def getInputFile():
            if self.inputFormatVar.get(): # input takes a directory
                self.input_file = filedialog.askdirectory(initialdir=os.getcwd())
                maskFormat.configure(state=NORMAL)
            else:
                self.input_file = filedialog.askopenfilename(initialdir=os.getcwd(), title="Input File Path", filetypes=(("nifti files", "*.nii"), ("nifti files", "*.nii.gz"), ("gifti files", "*.gii"), ("gifti files", "*.gii.gz")))
                maskFormat.configure(state=DISABLED)
                try:
                    self.file_type = os.path.splitext(self.input_file)[1]
                except: 
                    self.file_type = ()             
            try: 
                inputFileLabel.configure(text=self.input_file.split('/')[-1])
            except:
                inputFileLabel.configure(text="")

        def maskFormatButtonState():
            if self.maskFormatVar.get():
                maskFormatButton.configure(state=DISABLED)
            else:
                maskFormatButton.configure(state=NORMAL)

        def inputFormatButtonState():
            if self.inputFormatVar.get():
                maskFormat.configure(state=NORMAL)
            else:
                maskFormat.configure(state=DISABLED)
            maskFormatButtonState()

        def getMaskFile():
            self.mask_file = filedialog.askopenfilename(initialdir=os.getcwd(), title="Input File Path", filetypes=(("nifti files", "*.nii"), ("nifti files", "*.nii.gz"), ("gifti files", "*.gii"), ("gifti files", "*.gii.gz")))
            try:
                maskFileLabel.configure(text=self.mask_file.split("/")[-1])
            except:
                maskFileLabel.configure(text="")

        def getOutputDir():
            self.output_dir = filedialog.askdirectory(initialdir=os.getcwd())
            try:
                outputPathLabel.configure(text="Output path: " + self.output_dir.split("/")[-1])
            except:
                outputPathLabel.configure(text="")

        # defining widgets
        inputFormat        = Checkbutton(window, text="BIDS Format",       variable=self.inputFormatVar,                command=inputFormatButtonState)
        maskFormat         = Checkbutton(window, text="Mask File in BIDS", variable=self.maskFormatVar, state=DISABLED, command=maskFormatButtonState)
        inputFormatButton  = Button     (window, text="Select Input",                                                   command=getInputFile, height=1, width=20)
        maskFormatButton   = Button     (window, text="Select Mask File",                               state=NORMAL,   command=getMaskFile,  height=1, width=20)
        outputPathButton   = Button     (window, text="Select Output Directory",                                        command=getOutputDir, height=1, width=20)
        estimationLabel    = Label      (window, text="Estimation Rule: ")
        inputFileLabel     = Label      (window, text="")
        maskFileLabel      = Label      (window, text="")
        outputPathLabel    = Label      (window, text="")
        estimationDropDown = OptionMenu (window, self.estimationOption, "canon2dd", "sFIR", "FIR", "gamma", "fourier", "fourier w/ hanning")
        # placing widgets
        inputFormat.grid       (row=0,column=0,padx=(5,5),pady=(5,5))
        inputFormatButton.grid (row=0,column=1,padx=(5,5),pady=(5,5))
        inputFileLabel.grid    (row=1,column=0,padx=(5,5),pady=(5,5),columnspan=2)
        maskFormat.grid        (row=2,column=0,padx=(5,5),pady=(5,5))
        maskFormatButton.grid  (row=2,column=1,padx=(5,5),pady=(5,5))
        maskFileLabel.grid     (row=3,column=0,padx=(5,5),pady=(5,5),columnspan=2)
        outputPathButton.grid  (row=4,column=1,padx=(5,5),pady=(5,5))
        outputPathLabel.grid   (row=4,column=0,padx=(5,5),pady=(5,5))
        estimationLabel.grid   (row=5,column=0,padx=(5,5),pady=(5,5))
        estimationDropDown.grid(row=5,column=1,padx=(5,5),pady=(5,5))

    def getInput(self):
        if self.inputFormatVar.get() * self.maskFormatVar.get():
            mode = "bids"
        elif self.inputFormatVar.get():
            mode = "bids w/ atlas"
        else:
            mode = "file"
        return (self.input_file, self.mask_file, self.file_type, mode, self.estimationOption.get(), self.output_dir)