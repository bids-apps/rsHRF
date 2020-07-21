import numpy as np
import scipy.io
from scipy import stats
import matplotlib.pyplot as plt

def compare(num, with_plots=False):
    Name = ['Canonical HRF (with time derivative)', 'Canonical HRF (with time and dispersion derivatives)',
            'Gamma functions', 'Fourier set', 'Fourier set (Hanning)', \
            'FIR', 'sFIR']

    name = "./Data/hrf_" + Name[num] + "_"
    pythonPath = name + "python.txt"
    matlabPath = name + "matlab.mat"

    x = (np.loadtxt(pythonPath, delimiter=", ").T)
    y = scipy.io.loadmat(matlabPath)["hrfa"]
    if 'FIR' in name:
        y = y[:-1,:]
    x = np.expand_dims(x, axis=1)
    print(Name[num], ": ", stats.pearsonr(x[:,0],y[:,0])[0])

    if with_plots:
        plt.plot(x)
        plt.plot(y)
        plt.legend(["python", "matlab"], loc ="upper right")
        plt.show()

if __name__ == "__main__":
    for i in range(0, 7):
        compare(i)