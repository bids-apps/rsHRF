import sys
import numpy   as np
import os.path as op
from argparse      import ArgumentParser
from bids.grabbids import BIDSLayout

from rsHRF      import spm_dep, fourD_rsHRF

import warnings
warnings.filterwarnings("ignore")

with open(op.join(op.dirname(op.realpath(__file__)), "VERSION"), "r") as fh:
    __version__ = fh.read().strip('\n')

def get_parser():
    parser = ArgumentParser(description='retrieves the onsets of pseudo-events triggering a '
                                        'haemodynamic response from resting state fMRI BOLD '
                                        'voxel-wise signal')

    group_input = parser.add_mutually_exclusive_group(required=True)

    group_input.add_argument('--ts', action='store', type=op.abspath,
                             help='the absolute path to a single data file')

    group_input.add_argument('--input_file', action='store', type=op.abspath,
                             help='the absolute path to a single data file')

    group_input.add_argument('--bids_dir', nargs='?', action='store', type=op.abspath,
                             help='the root folder of a BIDS valid dataset '
                                  '(sub-XXXXX folders should be found at the '
                                  'top level in this folder).')

    group_input.add_argument('--GUI', action='store_true',
                            help='to execute the toolbox in GUI mode')

    parser.add_argument('--output_dir', action='store', type=op.abspath,
                        help='the output path for the outcomes of processing')

    parser.add_argument('--n_jobs', action='store', type=int, default=-1,
                        help='the number of parallel processing elements')

    parser.add_argument('-V', '--version', action='version', version='rsHRF version {}'.format(__version__))

    parser.add_argument('--analysis_level', help='Level of the analysis that will be performed. '
                        'Multiple participant level analyses can be run independently '
                        '(in parallel) using the same output_dir.', choices=['participant'], nargs='?')

    parser.add_argument('--participant_label',
                        help='The label(s) of the participant(s) that should be analyzed. The label '
                             'corresponds to sub-<participant_label> from the BIDS spec '
                             '(so it does not include "sub-"). If this parameter is not '
                             'provided all subjects should be analyzed. Multiple '
                             'participants can be specified with a space separated list.',
                        nargs="+")

    group_mask = parser.add_mutually_exclusive_group(required=False)

    group_mask.add_argument('--atlas', action='store', type=op.abspath,
                            help='the absolute path to a single atlas file')

    group_mask.add_argument('--brainmask', action='store_true',
                            help='to enable the use of mask files present in the BIDS '
                                 'directory itself')

    group_para = parser.add_argument_group('Parameters')

    group_para.add_argument('--estimation', action='store',
                            choices=['canon2dd', 'sFIR', 'FIR', 'fourier', 'hanning', 'gamma'],
                            help='Choose the estimation procedure from '
                                 'canon2dd (canonical shape with 2 derivatives), '
                                 'sFIR (smoothed Finite Impulse Response), '
                                 'FIR (Finite Impulse Response), '
                                 'fourier (Fourier Basis Set), '
                                 'hanning (Fourier Basis w Hanning), '
                                 'gamma (Gamma Basis Set)')

    group_para.add_argument('--passband', action='store', type=float, nargs=2, metavar=('LOW_FREQ','HIGH_FREQ'),
                            default=[0.01, 0.08],
                            help='set intervals for bandpass filter, default is 0.01 - 0.08')

    group_para.add_argument('--passband_deconvolve', action='store', type=float, nargs=2, metavar=('LOW_FREQ', 'HIGH_FREQ'),
                            default=[0.0, sys.float_info.max],
                            help='set intervals for bandpass filter (used while deconvolving BOLD), default is no-filtering')

    group_para.add_argument('-TR', action='store', type=float, default=-1,
                            help='set TR parameter')

    group_para.add_argument('-T', action='store', type=int, default=3,
                            help='set T parameter')

    group_para.add_argument('-T0', action='store', type=float, default=3,
                            help='set T0 parameter')

    group_para.add_argument('-TD_DD', action='store', type=int, default=2,
                            help='set TD_DD parameter')

    group_para.add_argument('-AR_lag', action='store', type=int, default=1,
                            help='set AR_lag parameter')

    group_para.add_argument('--thr', action='store', type=float, default=1,
                            help='set thr parameter')

    group_para.add_argument('--order', action='store', type=int, default=3,
                            help='set the number of basis vectors')

    group_para.add_argument('--len', action='store', type=int, default=24,
                            help='set len parameter')

    group_para.add_argument('--min_onset_search', action='store', type=int, default=4,
                            help='set min_onset_search parameter')

    group_para.add_argument('--max_onset_search', action='store', type=int, default=8,
                            help='set max_onset_search parameter')

    group_para.add_argument('--localK', action='store', type=int,
                            help='set localK')

    return parser


def run_rsHRF():
    parser = get_parser()

    args = parser.parse_args()

    arg_groups = {}

    for group in parser._action_groups:
        group_dict = {a.dest: getattr(args, a.dest, None) for a in group._group_actions }
        arg_groups[group.title] = group_dict

    para = arg_groups['Parameters']

    nargs = len(sys.argv)

    if (not args.GUI) and (args.output_dir is None):
        parser.error('--output_dir is required when executing in command-line interface')

    if (not args.GUI) and (args.estimation is None):
        parser.error('--estimation rule is required when executing in command-line interface')

    if (args.GUI):
        if (nargs == 2):
            try:
                from .rsHRF_GUI import run 
                run.run()
            except ModuleNotFoundError:
                parser.error('--GUI should not be used inside a Docker container')
        else:
            parser.error('--no other arguments should be supplied with --GUI')

    if (args.input_file is not None or args.ts is not None) and args.analysis_level:
        parser.error('analysis_level cannot be used with --input_file or --ts, do not supply it')

    if (args.input_file is not None or args.ts is not None) and args.participant_label:
        parser.error('participant_labels are not to be used with --input_file or --ts, do not supply it')

    if args.input_file is not None and args.brainmask:
        parser.error('--brainmask cannot be used with --input_file, use --atlas instead')

    if args.ts is not None and (args.brainmask or args.atlas):
        parser.error('--atlas or --brainmask cannot be used with --ts, do not supply it')

    if args.bids_dir is not None and not (args.brainmask or args.atlas):
        parser.error('--atlas or --brainmask needs to be supplied with --bids_dir')

    if args.bids_dir is not None and not args.analysis_level:
        parser.error('analysis_level needs to be supplied with bids_dir, choices=[participant]')

    if args.input_file is not None and (not args.input_file.endswith(('.nii', '.nii.gz', '.gii', '.gii.gz'))):
        parser.error('--input_file should end with .gii, .gii.gz, .nii or .nii.gz')

    if args.atlas is not None and (not args.atlas.endswith(('.nii', '.nii.gz','.gii', '.gii.gz'))):
        parser.error('--atlas should end with .gii, .gii.gz, .nii or .nii.gz')

    if args.ts is not None and (not args.ts.endswith(('.txt'))):
        parser.error('--ts file should end with .txt')

    if args.ts is not None:
        file_type = op.splitext(args.ts)
        if para['TR'] <= 0:
            parser.error('Please supply a valid TR using -TR argument')
        else:
            TR = para['TR']
        para['dt'] = para['TR'] / para['T']
        para['lag'] = np.arange(np.fix(para['min_onset_search'] / para['dt']),
                                np.fix(para['max_onset_search'] / para['dt']) + 1,
                                dtype='int')
        fourD_rsHRF.demo_rsHRF(args.ts, None, args.output_dir, para, args.n_jobs, file_type, mode='time-series')

    if args.input_file is not None:
        if args.atlas is not None:
            if (args.input_file.endswith(('.nii', '.nii.gz')) and args.atlas.endswith(('.gii', '.gii.gz'))) or (args.input_file.endswith(('.gii', '.gii.gz')) and args.atlas.endswith(('.nii', '.nii.gz'))):
                parser.error('--atlas and input_file should be of the same type [NIfTI or GIfTI]')
        
        # carry analysis with input_file and atlas
        file_type = op.splitext(args.input_file)
        if file_type[-1] == ".gz":
            file_type = op.splitext(file_type[-2])[-1] + file_type[-1]
        else:
            file_type = file_type[-1]
        if ".nii" in file_type:
            TR = (spm_dep.spm.spm_vol(args.input_file).header.get_zooms())[-1]
        else:
            if para['TR'] == -1:
                parser.error('Please supply a valid TR using -TR argument')
            else:
                TR = para['TR']
        if TR <= 0:
            if para['TR'] <= 0:
                parser.error('Please supply a valid TR using -TR argument')
        else:
            if para['TR'] == -1:
                para['TR'] = TR
            elif para['TR'] <= 0:
                print('Invalid TR supplied, using implicit TR: {0}'.format(TR))
                para['TR'] = TR
        para['dt'] = para['TR'] / para['T']
        para['lag'] = np.arange(np.fix(para['min_onset_search'] / para['dt']),
                                np.fix(para['max_onset_search'] / para['dt']) + 1,
                                dtype='int')
        fourD_rsHRF.demo_rsHRF(args.input_file, args.atlas, args.output_dir, para, args.n_jobs, file_type, mode='input')

    
    if args.bids_dir is not None and args.atlas is not None:
        # carry analysis with bids_dir and 1 atlas
        layout = BIDSLayout(args.bids_dir)

        if args.participant_label:
            input_subjects = args.participant_label
            subjects_to_analyze = layout.get_subjects(subject=input_subjects)
        else:
            subjects_to_analyze = layout.get_subjects()

        if not subjects_to_analyze:
            parser.error('Could not find participants. Please make sure the BIDS data '
                         'structure is present and correct. Datasets can be validated online '
                         'using the BIDS Validator (http://incf.github.io/bids-validator/).')

        if not args.atlas.endswith(('.nii', '.nii.gz')):
            parser.error('--atlas should end with .nii or .nii.gz')

        all_inputs = layout.get(modality='func', subject=subjects_to_analyze, task='rest', type='preproc', extensions=['nii', 'nii.gz'])
        if not all_inputs != []:
            parser.error('There are no files of type *preproc.nii / *preproc.nii.gz '
                         'Please make sure to have at least one file of the above type '
                         'in the BIDS specification')
        else:
            num_errors = 0
            for file_count in range(len(all_inputs)):
                try:
                    TR = layout.get_metadata(all_inputs[file_count].filename)['RepetitionTime']
                except KeyError as e:
                    TR = spm_dep.spm.spm_vol(all_inputs[file_count].filename).header.get_zooms()[-1]
                para['TR'] = TR
                para['dt'] = para['TR'] / para['T']
                para['lag'] = np.arange(np.fix(para['min_onset_search'] / para['dt']),
                                        np.fix(para['max_onset_search'] / para['dt']) + 1,
                                        dtype='int')
                num_errors += 1
                try:
                    fourD_rsHRF.demo_rsHRF(all_inputs[file_count], args.atlas, args.output_dir, para, args.n_jobs, file_type, mode='bids w/ atlas')
                    num_errors -=1
                except ValueError as err:
                    print(err.args[0])
                except:
                    print("Unexpected error:", sys.exc_info()[0])
            success = len(all_inputs) - num_errors
            if success == 0:
                raise RuntimeError('Dimensions were inconsistent for all input-mask pairs; \n'
                                   'No inputs were processed!')

    if args.bids_dir is not None and args.brainmask:
        # carry analysis with bids_dir and brainmask
        layout = BIDSLayout(args.bids_dir)

        if args.participant_label:
            input_subjects = args.participant_label
            subjects_to_analyze = layout.get_subjects(subject=input_subjects)
        else:
            subjects_to_analyze = layout.get_subjects()

        if not subjects_to_analyze:
            parser.error('Could not find participants. Please make sure the BIDS data '
                         'structure is present and correct. Datasets can be validated online '
                         'using the BIDS Validator (http://incf.github.io/bids-validator/).')

        all_inputs = layout.get(modality='func', subject=subjects_to_analyze, task='rest', type='preproc', extensions=['nii', 'nii.gz'])
        all_masks = layout.get(modality='func', subject=subjects_to_analyze, task='rest', type='brainmask', extensions=['nii', 'nii.gz'])
        if not all_inputs != []:
            parser.error('There are no files of type *preproc.nii / *preproc.nii.gz '
                         'Please make sure to have at least one file of the above type '
                         'in the BIDS specification')
        if not all_masks != []:
            parser.error('There are no files of type *brainmask.nii / *brainmask.nii.gz '
                         'Please make sure to have at least one file of the above type '
                         'in the BIDS specification')
        if len(all_inputs) != len(all_masks):
            parser.error('The number of *preproc.nii / .nii.gz and the number of '
                         '*brainmask.nii / .nii.gz are different. Please make sure that '
                         'there is one mask for each input_file present')

        all_inputs.sort()
        all_masks.sort()

        all_prefix_match = False
        prefix_match_count = 0
        for i in range(len(all_inputs)):
            input_prefix = all_inputs[i].filename.split('/')[-1].split('_preproc')[0]
            mask_prefix = all_masks[i].filename.split('/')[-1].split('_brainmask')[0]
            if input_prefix == mask_prefix:
                prefix_match_count += 1
            else:
                all_prefix_match = False
                break
        if prefix_match_count == len(all_inputs):
            all_prefix_match = True

        if not all_prefix_match:
            parser.error('The mask and input files should have the same prefix for correspondence. '
                         'Please consider renaming your files')
        else:
            num_errors = 0
            for file_count in range(len(all_inputs)):
                file_type = op.splitext(all_inputs[file_count].filename)[1]
                if file_type == ".nii" or file_type == ".nii.gz":
                    try:
                        TR = layout.get_metadata(all_inputs[file_count].filename)['RepetitionTime']
                    except KeyError as e:
                        TR = spm_dep.spm.spm_vol(all_inputs[file_count].filename).header.get_zooms()[-1]
                    para['TR'] = TR
                else:
                    spm_dep.spm.spm_vol(all_inputs[file_count].filename)
                    TR = spm_dep.spm.spm_vol(all_inputs[file_count].filename).get_arrays_from_intent("NIFTI_INTENT_TIME_SERIES")[0].meta.get_metadata()["TimeStep"]
                    para['TR'] = float(TR) * 0.001


                para['dt'] = para['TR'] / para['T']
                para['lag'] = np.arange(np.fix(para['min_onset_search'] / para['dt']),
                                        np.fix(para['max_onset_search'] / para['dt']) + 1,
                                        dtype='int')
                num_errors += 1
                try:
                    fourD_rsHRF.demo_rsHRF(all_inputs[file_count], all_masks[file_count], args.output_dir, para, args.n_jobs, mode='bids')
                    num_errors -=1
                except ValueError as err:
                    print(err.args[0])
                except:
                    print("Unexpected error:", sys.exc_info()[0])
            success = len(all_inputs) - num_errors
            if success == 0:
                raise RuntimeError('Dimensions were inconsistent for all input-mask pairs; \n'
                                   'No inputs were processed!')
                


def main():
    warnings.filterwarnings("ignore")
    run_rsHRF()


if __name__ == '__main__':
    raise RuntimeError("CLI.py should not be run directly;\n"
                       "Please `pip install` rsHRF and use the `rsHRF` command")
