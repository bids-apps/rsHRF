# Testing rsHRF Toolbox

### Parameters
All the parameters are provided in /Data/Input/parameters.dat file.
The parameters are as follows:
1. Estimation Rule (according to the list in matlab, i.e. 4 corresponds to Fourier Set)
2. para.order 
3. para.TR
4. para.passband.lhs
5. para.passband.rhs
6. para.T
7. para.T0
8. min_onset_search
9. max_onset_search
10. para.AR_lag
11. para.thr
12. para.len
13. voxel id 


## Step-1 : Upto Retrieving the resting-state Hemodynamic Respnse Function

### Test-1
1. TR = 2 
2. AR_lag = 0
3. T = 1
4. No Volterra
5. Using volume
6. sub-1071_task-rest_bold_space-MNI152NLin2009cAsym_preproc

**Random Voxel**
Canonical HRF (with time derivative) :  0.9879043534521337
Canonical HRF (with time and dispersion derivatives) :  0.8854829499439278
Gamma functions :  0.9848671050994082
Fourier set :  0.9952499785201516
Fourier set (Hanning) :  0.9988925086859511

T=2
AR_lag=0
**Random Voxel**
Canonical HRF (with time derivative) :  0.9874449112341122
Canonical HRF (with time and dispersion derivatives) :  0.8911316655498438
Gamma functions :  0.9481064461553852
Fourier set :  0.8820407688572847
Fourier set (Hanning) :  0.8784108075669139

T=3
AR_lag=0
**Random Voxel**
Canonical HRF (with time derivative) :  0.999991155080374
Canonical HRF (with time and dispersion derivatives) :  0.8906769746638721
Gamma functions :  0.8791847098694174
Fourier set :  0.7797787015564639
Fourier set (Hanning) :  0.795625374573464

T=5
AR_lag=0
**Random Voxel**
Canonical HRF (with time derivative) :  0.9928769428599366
Canonical HRF (with time and dispersion derivatives) :  0.8841503676640108
Gamma functions :  0.8296380346200087
Fourier set :  0.6767847405489411
Fourier set (Hanning) :  0.7225710960149432

T=1
AR_lag=5
Canonical HRF (with time derivative) :  0.9755950271801934
Canonical HRF (with time and dispersion derivatives) :  0.9456994696776716
Gamma functions :  0.8786689503931939
Fourier set :  0.7217490419569943
Fourier set (Hanning) :  0.6985432601907688

T=1
AR_lag=1
Canonical HRF (with time derivative) :  0.9999999999999999
Canonical HRF (with time and dispersion derivatives) :  0.9446739277567662
Gamma functions :  1.0
Fourier set :  1.0
Fourier set (Hanning) :  1.0

T=1
AR_lag=2
Canonical HRF (with time derivative) :  0.990875287246731
Canonical HRF (with time and dispersion derivatives) :  0.9458342694617542
Gamma functions :  0.9033014540542614
Fourier set :  0.9994961179031248
Fourier set (Hanning) :  0.9922269667890173

T=2
AR_lag=2
Canonical HRF (with time derivative) :  0.9407965128275381
Canonical HRF (with time and dispersion derivatives) :  0.9533197192755819
Gamma functions :  0.8825398116874779
Fourier set :  0.9380171133323485
Fourier set (Hanning) :  0.972424928556854

T=1
AR_lag=3
Canonical HRF (with time derivative) :  0.9782416727063137
Canonical HRF (with time and dispersion derivatives) :  0.9441008383875434
Gamma functions :  0.9544577303726169
Fourier set :  0.9241324813159797
Fourier set (Hanning) :  0.8813968908601999