clc,clear;close all;
warning off all
addpath /home/redhood/Applications/spm12
addpath /home/redhood/Desktop/Work/GSoC/rsHRF-Toolbox/rsHRF-master
addpath /home/redhood/Desktop/Work/GSoC/rsHRF-Toolbox/rsHRF-master/demo_code
savepath 
BF = {'Canonical HRF (with time derivative)'
'Canonical HRF (with time and dispersion derivatives)'              
'Gamma functions'
'Fourier set'
'Fourier set (Hanning)'};

parameters = load('./Data/Input/parameters.dat');

para.name = BF{parameters(1)}; % using canonical HRF with time and dispersion derivatives
para.order = parameters(2); % for Gamma functions or Fourier set

temporal_mask = []; % without mask, it means temporal_mask = ones(nobs,1); i.e. all time points included. nobs: number of observation = size(data,1). if want to exclude the first 1~5 time points, let temporal_mask(1:5)=0;

TR = parameters(3); % THIS WILL BE READ FROM THE BIDS DATA

para.TR = TR;
para.passband=[parameters(4) parameters(5)]; %bandpass filter lower and upper bound

%%% the following parameter (upsample grid) can be > 1 only for Canonical.
para.T  = parameters(6); % magnification factor of temporal grid with respect to TR. i.e. para.T=1 for no upsampling, para.T=3 for 3x finer grid

para.T0 = parameters(7); % position of the reference slice in bins, on the grid defined by para.T. For example, if the reference slice is the middle one, then para.T0=fix(para.T/2)
if para.T==1
    para.T0 = 1;
end


min_onset_search = parameters(8); % minimum delay allowed between event and HRF onset (seconds)
max_onset_search = parameters(9); % maximum delay allowed between event and HRF onset (seconds)

para.dt  = para.TR/para.T; % fine scale time resolution.

para.AR_lag = parameters(10); % AR(1) noise autocorrelation.

para.thr = parameters(11); % (mean+) para.thr*standard deviation threshold to detect event.

para.len = parameters(12); % length of HRF, in seconds

para.lag  = fix(min_onset_search/para.dt):fix(max_onset_search/para.dt);

%%===================================

%%===========fMRI Data========================

path = '/home/redhood/Desktop/Work/GSoC/rsHRF-Toolbox/rsHRF-GUI/Input/';
inputFilePath = strcat(path,'sub-031274_task-rest_bold.nii');
maskFilePath = strcat(path,'sub-031274_task-rest_bold_brain.nii');

v = niftiread(inputFilePath);
v0 = niftiread(maskFilePath);

v = reshape(v,64*64*32,242);
v0 = reshape(v0,64*64*32,1);
ind = find(v0>0);
bold_sig_arr = double(v(ind,:));
[r, c]=size(bold_sig_arr);
hrfa_arr = zeros(37,25613);
tic
for i=1:r
    bold_sig = bold_sig_arr(i,:);
    bold_sig = bold_sig';
    nobs = size(bold_sig,1);
    bold_sig = zscore(bold_sig);
    bold_sig = rest_IdealFilter(bold_sig, para.TR, para.passband);

    [beta_hrf, bf, event_bold] = rsHRF_estimation_temporal_basis(bold_sig,para,temporal_mask);
    hrfa = bf*beta_hrf(1:size(bf,2),:); %HRF
    
    hrfa_arr(:,i) = hrfa;
   
end
toc
disp('Done');

save(strcat('./Data/matlab_',BF{parameters(1)},'.mat'))


