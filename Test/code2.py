import scipy.io
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

curr = (np.loadtxt("hrfa_current_fourier.txt", delimiter=", ").T)
curr_kenzo = (np.loadtxt("hrfa_current_fourier_kenzo.txt", delimiter=", ").T)
matlab = scipy.io.loadmat("hrfa_fourier.mat")["hrfa_arr"].T

x = curr_kenzo
y = matlab

arr = []
for i in range(x.shape[0]):
    arr.append(stats.pearsonr(x[i],y[i])[0])
arr = np.asarray(arr)
print("Maximum: ", np.max(arr))
print("Minimum: ", np.min(arr))
print("Mean: ", np.mean(arr))
print("Standard Deviation: ", np.std(arr))