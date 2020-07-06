import numpy as np
import scipy.io
from scipy import stats
import matplotlib.pyplot as plt

num = 2
Name = ['Gamma functions', 'Fourier set', 'Fourier set (Hanning)']

pythonPath = "./Data/hrf"+Name[num]+"_kenzo.txt"
matlabPath = "./Data/matlab_"+Name[num]+".mat"

x = (np.loadtxt(pythonPath, delimiter=", ").T)
y = scipy.io.loadmat(matlabPath)["hrfa_arr"].T

arr = []
for i in range(x.shape[0]):
    arr.append(stats.pearsonr(x[i],y[i])[0])
arr = np.asarray(arr)
print("Maximum: ", np.max(arr))
print("Minimum: ", np.min(arr))
print("Mean: ", np.mean(arr))
print("Standard Deviation: ", np.std(arr))

