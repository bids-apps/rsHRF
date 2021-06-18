"""Base module variables."""
from os import path as op

with open(op.join(op.dirname(op.realpath(__file__)), "VERSION"), "r") as fh:
    __version__ = fh.read().strip('\n')

__packagename__ = 'rsHRF'
__url__ = 'https://github.com/BIDSapps/rsHRF'

DOWNLOAD_URL = (
    'https://github.com/BIDS-Apps/{name}/'.format(
        name=__packagename__))