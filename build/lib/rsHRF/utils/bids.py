"""Utilities to handle BIDS inputs."""
import os
import sys
import json
from pathlib import Path

def write_derivative_description(bids_dir, deriv_dir):
    from ..__about__ import __version__, DOWNLOAD_URL

    print(__version__)
    bids_dir = Path(bids_dir)
    deriv_dir = Path(deriv_dir)
    desc = {
        'Name': 'rsHRF - retrieve the haemodynamic response function from resting state fMRI data',
        'BIDSVersion': '1.4.0',
        'DatasetType': 'derivative',
        'GeneratedBy': [{
            'Name': 'rsHRF',
            'Version': __version__,
            'CodeURL': DOWNLOAD_URL,
        }],
        'HowToAcknowledge':
            'Please cite our paper : https://doi.org/10.1016/j.neuroimage.2021.118591 '
            ,
    }

    # Keys that can only be set by environment
    if 'RSHRF_DOCKER_TAG' in os.environ:
        desc['GeneratedBy'][0]['Container'] = {
            "Type": "docker",
            "Tag": f"bids/rshrf:{os.environ['FMRIPREP_DOCKER_TAG']}"
        }
    if 'RSHRF_SINGULARITY_URL' in os.environ:
        desc['GeneratedBy'][0]['Container'] = {
            "Type": "singularity",
            "URI": os.getenv('FMRIPREP_SINGULARITY_URL')
        }

    # Keys deriving from source dataset
    orig_desc = {}
    fname = bids_dir / 'dataset_description.json'
    if fname.exists():
        orig_desc = json.loads(fname.read_text())

    if 'DatasetDOI' in orig_desc:
        desc['SourceDatasets'] = [{
            'URL': f'https://doi.org/{orig_desc["DatasetDOI"]}',
            'DOI': orig_desc['DatasetDOI']
        }]
    if 'License' in orig_desc:
        desc['License'] = orig_desc['License']

    Path.write_text(deriv_dir / 'dataset_description.json', json.dumps(desc, indent=4))
