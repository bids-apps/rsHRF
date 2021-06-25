
clc,clear;close all;

warning off all
addpath /home/redhood/Applications/spm12                                     % add the path to spm directory
addpath /home/redhood/Desktop/Work/GSoC-2020/rsHRF-Toolbox/rsHRF/Test/VoxelTest   % add the path to current directory
addpath /home/redhood/Desktop/Work/GSoC-2020/rsHRF-master           % add the path to rsHRF-master directory
addpath /home/redhood/Desktop/Work/GSoC-2020/rsHRF-Toolbox/demo_codes % add the path to rsHRF-master/demo_code
savepath 

% Create output folder
if ~exist('./Data','dir')
    mkdir('./Data')
end

% all the estimation rules
BF = {'Canonical HRF (with time derivative)'
'Canonical HRF (with time and dispersion derivatives)'            
'Gamma functions'
'Fourier set'
'Fourier set (Hanning)'
'FIR'
'sFIR'};

parameters = load('./parameters.dat');           % loading the parameters from file
para.order       = parameters(2);                % for Gamma functions or Fourier set
temporal_mask    = [];                           % without mask, it means temporal_mask = ones(nobs,1); i.e. all time points included. nobs: number of observation = size(data,1). if want to exclude the first 1~5 time points, let temporal_mask(1:5)=0;
para.TR          = parameters(3);                % BOLD repetition time
para.passband    =[parameters(4) parameters(5)]; %bandpass filter lower and upper bound
para.T           = parameters(6);                % magnification factor of temporal grid with respect to TR. i.e. para.T=1 for no upsampling, para.T=3 for 3x finer grid
para.T0          = parameters(7);                % position of the reference slice in bins, on the grid defined by para.T. For example, if the reference slice is the middle one, then para.T0=fix(para.T/2)
min_onset_search = parameters(8);                % minimum delay allowed between event and HRF onset (seconds)
max_onset_search = parameters(9);                % maximum delay allowed between event and HRF onset (seconds)
para.dt          = para.TR/para.T;               % fine scale time resolution.
para.AR_lag      = parameters(10);               % AR(1) noise autocorrelation.
para.thr         = parameters(11);               % (mean+) para.thr*standard deviation threshold to detect event.
para.len         = parameters(12);               % length of HRF, in seconds     
para.lag  = fix(min_onset_search/para.dt):fix(max_onset_search/para.dt);
if para.T==1
    para.T0 = 1;
end

voxel_id         = parameters(13) + 1;           % voxel to be analyzed

% looping over all the estimation rules
for counter = 1 : 7
para.name  = BF{counter};   % estimation rule
para.estimation = para.name;
%%===================================

%%===========fMRI Data===============
%path            = '/home/redhood/Desktop/Work/GSoC-2020/rsHRF/Test/NITRC-multi-file-downloads/sub-10171/func/'; % input directory 
inputFilePath   = strcat(path,'sub-10171_task-rest_bold_space-T1w_preproc.nii');
maskFilePath    = strcat(path,'sub-10171_task-rest_bold_space-T1w_brainmask.nii');

v = spm_read_vols(spm_vol((inputFilePath)));
v0 = spm_read_vols(spm_vol((maskFilePath)));
dim = size(v);
ntime = dim(4);
voxels = dim(1)*dim(2)*dim(3);
v = reshape(v,voxels,ntime);
v0 = reshape(v0,voxels,1);
ind = find(v0>0);
bold_sig_arr = double(v(ind,:));

tic

bold_sig = bold_sig_arr(voxel_id,:);
bold_sig = bold_sig';
nobs     = size(bold_sig,1);
bold_sig = zscore(bold_sig);

bold_sig = rsHRF_band_filter(bold_sig, para.TR, para.passband);

if counter < 6       % for temporal basis sets
    [beta_hrf, bf, event_bold] = rsHRF_estimation_temporal_basis(bold_sig,para,temporal_mask);
    hrfa = bf*beta_hrf(1:size(bf,2),:);
elseif counter >= 6 % for FIR and sFIR
    [beta_hrf,event_bold] = rsHRF_estimation_FIR(bold_sig,para,temporal_mask);
    hrfa = beta_hrf(1:end-2,:);
end


toc

disp('Done');
save(strcat('./Data/hrf_',BF{counter},'_matlab.mat'), 'hrfa');

end

