# Class-Structure Information

Here we have tried to define the purpose and usage of each class relavant to the rsHRF-GUI.

---

## rsHRF_GUI.core.Core

This class in concerned with all the technical data-processing w.r.t the rsHRF toolbox. 

### Class Variables
- `self.parameters` -  an instance of the Parameters() object
- `self.dataStre` - an instance of the Store() object

---

### Class Methods
- `updateParameters(self, dic={})` - takes a dictionary and updates the *self.parameters* variables. <br>
- `get_parameters(self)` - returns the rsHRF parameters as a dictionary
- `get_time_series(self, curr)` - returns the time-series object as defined by the string variable *curr*.
- `get_plotables(self, curr)` - returns the plotable artefact corresponding to the string variable *curr*.
- `get_store_info(self, curr)` - returns the information about the time-series object corresponding to the string variable *curr*.
- `get_subjects(self)` - returns a list of all the subjects that are present in the *self.dataStore*.
- `get_data_labels(self, curr)` - returns a label string corresponding to the string variable *curr*.
- `save_info(self, curr, out)` - save sthe info regarding the time-series corresponding to the variable *curr*, in the directory as specified using *out*.
- `makeInput(self, inp)` - takes different forms of input files and forms the *RAW-BOLD* and *Preprocessed-BOLD* time-series objects, and saves it with respect to their corresponding subjects in the *self.dataStore*.
- `makeInputFile(self, input_file, mask_file, file_type, mode)` - deals with one-input-instance at a time.
- `retrieveHRF(self, bold_pre_ts, get_pos=False)` - retrieves the rsHRF corresponding to a preprocessed-BOLD time-series.
- `getHRFParameters(self, hrf)` - computes the corresponding rsHRF parameters with respct to an HRF time-series.
- `deconvolveHRF(self, hrf)` - uses the retrieved rsHRF to deconvolve the preprocessed BOLD time-series.

---

## rsHRF_GUI.datatypes.misc.parameters.Parameters
This class corresponds to all the rsHRF-toolbox parameters.

### Class Variables
All the information regarding the class-variables can be found along with the main documentation of the rsHRF-toolbox.
- `self.estimation`
- `self.passband`
- `self.passband_deconvolve`
- `self.TR`
- `self.localK`
- `self.T`
- `self.T0`
- `self.TD_DD`
- `self.AR_lag`
- `self.thr`
- `self.order`
- `self.volterra`
- `self.len`
- `self.temporal_mask`
- `self.min_onset_search`
- `self.max_onset_search`
- `self.dt`
- `self.lag`

---

### Class Methods
**Getters**
- `get_estimation(self)`
- `get_passband(self)`
- `get_passband_deconvolve(self)`
- `get_TR(self)`
- `get_localK(self)`
- `get_T(self)`
- `get_T0(self)`
- `get_TD_DD(self)`
- `get_AR_lag(self)`
- `get_thr(self)`
- `get_order(self)`
- `get_volterra(self)`
- `get_len(self)`
- `get_temporal_mask(self)`
- `get_min_onset_search(self)`
- `get_max_onset_search(self)`
- `get_dt(self)`
- `get_lag(self)`

---

**Setters**

All the setters take the corresponding error-handling into account. If an illegal value is provided, a suitable error gets returned. <br>
Also, if setting there are variables that get affected by the one being set, the change gets propogated automatically.

- `set_estimation(self, var)`
- `set_passband(self, var)`
- `set_passband_deconvolve(self, var)`
- `set_TR(self, var)`
- `set_localK(self, var)`
- `set_T(self, var)`
- `set_T0(self, var)`
- `set_TD_DD(self, var)`
- `set_AR_lag(self, var)`
- `set_thr(self, var)`
- `set_order(self, var)`
- `set_volterra(self, var)`
- `set_len(self, var)`
- `set_temporal_mask(self, var)`
- `set_min_onset_search(self, var)`
- `set_max_onset_search(self, var)`

---

These parameters are dependent parameters, and hence, these are automatically updates as and when required.

- `update_dt(self)`
- `update_lag(self)`

---

- `get_parameters(self)` - returns all the parameters as a dictionary.
- `set_parameters(self, dic)` - takes a dictionary as input and sets the parameters.
- `compareParameters(self, p)` - takes another *parameters* object and compares whether it is similar as this parameters object or not. 

--- 

## rsHRF_GUI.datatypes.misc.store.Store
This corresponds to where all the *subject* objects are dealt with.

### Class Variables

- `self.subjects` - a dictionary which stores the subjects against their labels (the labels are the string value as in BIDS format).

---

### Class Methods

- `get_subjects(self)` - returns the labels for all the subjects.
- `get_subject_by_index(self, index)` - takes the subject index and returns the subject object.
- `get_plotables(self, index)` - takes the subject index and returns all the plotables artefats associated to that subject.
- `get_data_labels(self, index)` - returns labels for all the relavant artefacts corresponding to the subject given by the index.
- `get_time_series(self, s)` - returns the time-series object corresponding to the string *s*.
- `get_info(self, s)` - return the information regarding the time-series object corresponding to the string *s*. 
- `is_present(self, subject_index)` - checks whether the subject corresponding to an index value is already present.
- `add_subject(self, sub)` - takes a *subject* object and adds it into the store.
- `remove_subject(self, sub)` - takes a *subject* object and removes it from the store.
- `number_of_subjects(self)` - returns the number of subjects corrently in the store.
- `save_info(self, s, out)` - saves the information regarding the subject as denoted by *s*, into the directory corresponding to *out*.

---

## rsHRF_GUI.datatypes.misc.subject.Subject
This corresponds to every individual subject.

### Class Variables
- `self.index` - index of the subject (as in BIDS format)
- `self.BOLD_raw` - list of all the RAW BOLD time-series data.
- `self.BOLD_pre` - list of the preprocessed BOLD time-series data.
- `self.BOLD_deconv` - list of all the deconvolved BOLD time-series data.
- `self.HRF` - list of all the HRF time-series data.

---

### Class Methods
**Getters**
- `get_input_filename(self)` 
- `get_subject_index(self)`
- `get_BOLD_raw(self)`
- `get_BOLD_pre(self)`
- `get_BOLD_deconv(self)`
- `get_HRF(self)`

--- 

**Adding Data**

Adds time-series data to the existing collection.

- `add_BOLD_raw(self, ts)`
- `add_BOLD_deconv(self, ts)`
- `add_BOLD_pre(self, ts)`
- `add_HRF(self, ts)`

---

- `is_present(self, label, misc, getts=False)` - checks whether a time-series object is already present or not.
- `get_time_series_pas(self, ts)` - gets the position of the time-series object in the list that it is stored.
- `get_time_series_by_index(self, ts_type, index)` - gets the time-series object as specified by the *index*.
- `get_plotables(self)` - returns all the plotable time-series artefacts.
- `get_data_labels(self)` - returns the lables for all the time-series artefacts.

--- 

## rsHRF_GUI.datatypes.timeseries.TimeSeries
This deals with the time-series objects.
### Class Variables
- `self.label` - label of the time-series
- `self.subject_index` - subject-index of the subject that the time-series is associated to.
- `self.timeseries` - the time-series stored as a numpy array.
- `self.shape` - shape of the time-series
- `self.parameters` - rsHRF parameters required while obtaining the time-series.

---

### Class Methods
** Setters **
- `set_ts(self, ts)`
- `set_parameters(self, para)`
- `set_label(self, label)`
- `set_subject_index(self, subject_index)`
  
---

** Getters *8
- `get_ts(self)`
- `get_subject_index(self)` 
- `get_label(self)`
- `get_parameters(self)`
- `get_shape(self)`
- `get_info(self)`

---

- `compareTimeSeries(self, ts)` - compares the two-timeseries to figure out whether they are identicle.
- `save_info(self, name)` - saves the information of the time-series in a .mat file.

---

**Note:** The *rsHRF_GUI.datatypes.timeseries* package contains other classes: 
<br>
1. Bold_Deconv
2. Bold_Preprocessed
3. Bold_Raw
4. HRF

All these classes inherit from the time-series classes, and suitable class variables, getters, setters, are added, and appropriate functions are overridden. However, the basic structure for all these classes remains the same.

---

## rsHRF_GUI.misc.status.Status

This class allows for making the GUI more interactive. It provides an inherent way of communication across the different modules.

### Class Variables
- `self.state` - a boolean value
- `self.info` - information string regarding the message
- `self.error` - error string corresponding to the message
- `self.time` - stores the time of the message
- `self.dic` - a dictionary for storing misc. information about the message

---

### Class Methods
** Setters **
- `set_state(self, s)`
- `set_info(self, s)`
- `set_error(self, e)`
- `set_time(self, t)`
- `set_dic(self, d)`

---

** Getters **
- `get_state(self)`
- `get_info(self)`
- `get_error(self)`
- `get_time(self)`
- `get_dic(self)`

---

## rsHRF_GUI.misc.gui_windows.inputWindow.InputWindow

This class is concerned with accepting the input, determining whether its in a valid format, and subsequently passing a valid input forward.

### Class Variables
- `self.input_file` - stores the path to input file
- `self.mask_file` - stores the path to mask file
- `self.file_type` - stores the type of the file
- `self.output_dir` - stores the path to the output directory

--- 

### Class Methods

- `getInput(self)` - retrieves the input from the GUI and passes it to `main.py`

--- 

## rsHRF_GUI.misc.gui_windows.loggingWindow.LoggingWindow

### Class Variables
- `self.lineNum` - the position of the current line in the logging window
- `self.text` - ScrolledText window

---

### Class Methods
- `putLog(self, plotables=None, data_info=None, status=None)` - depending upon the input, appropriately formats it and displays it on the logging-screen.

---

## rsHRF_GUI.misc.gui_windows.parameterWindow.ParameterWindow

### Class Variables
- `self.window` - Toplevel instance
- `self.parameters` - dictionary containing all the rsHRF parameters
- `self.labels` - labels corresponding to each parameter
- `self.entries` - current value of each parameter

---

### Class Methods
- `updateParameters(self)` - updates the parameter dictionary
- `getParameters(self)` - gets the parameter dictionary
- `setParameters(self)` - sets the parameter dictionary
- `display(self)` - puts the elements of the parameter dictionary into *self.labels* and *self.entries* in a way that they can be displayed by the logging-window.

--- 

## rsHRF_GUI.misc.gui_windows.plotterOptionsWindow.PlotterOptionsWindow

### Class Variables
- `self.plotterScreen` - PlotterWindow instance
- `self.numberOfPlots` - the number of plots on the plotter-screen
- `self.plot` - string corresponding to the time-series which is to be plotted
- `self.plotVal` - voxel value of the time-series that is to be plotted
- `self.plotValStore` - decides whether the current plot is to be displayed or not
- `self.plotables` - list of strings corresponding to all the time-series that can be plotted
- `self.options` - to display the various plots that can be plotted in the drop-down menu

---

### Class Methods
- `updatePlots(self, plotables)` - takes an iterable (plotables) and reconfigures the various time-series  that can be plotted
- `updateWidgets(self)` - updates the widgets on the *plotter-window*
- `get_plotables(self)` - returns the plotables

--- 

## rsHRF_GUI.misc.gui_windows.plotterWindow.PlotterWindow

### Class Variables 
- `self.numberOfPlots` - the number of plots that can be displayed at a time (right now = 3)
- `self.ts` - list of time-series that are to be plotted
- `self.plot` - displaying the plots
- `self.canvas` - FigureCanvasTkAgg instance

---

### Class Methods
- `getNumberOfPlots(self)` - gives the number of plots
- `makePlots(self, ts, val, num)` - displays the appropriate plots

---

## Fin.