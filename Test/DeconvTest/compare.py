import os 
import shutil
import numpy as np 
import scipy.io
import matplotlib.pyplot as plt 
from deconv import rsHRF_iterative_wiener_deconv

import warnings
warnings.filterwarnings("ignore")

d = scipy.io.loadmat('data.mat')
xwiener = rsHRF_iterative_wiener_deconv(d["bold"], d["hrf"])
xwienerM = scipy.io.loadmat('result_matlab.mat')['xwiener']
plt.plot(abs(d["bold"].reshape(-1)))
plt.title("BOLD Signal")
plt.show()
plt.plot(d["hrf"].reshape(-1))
plt.title("HRF")
plt.show()
plt.plot(xwiener)
plt.plot(xwienerM)
plt.legend(["Python", "Matlab"])
plt.show()
try: shutil.rmtree("__pycache__")
except: pass