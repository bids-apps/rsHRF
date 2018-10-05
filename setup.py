import re
import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install

with open("rsHRF/VERSION", "r") as fh:
    VERSION = fh.read().strip('\n')

with open("README.md", "r") as fh:
    long_description = fh.read()

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)    
    
setup(
    name="rsHRF",
    packages=find_packages(),
    entry_points={
        "console_scripts": ['rsHRF = rsHRF.CLI:main']
    },
    version=VERSION,
    description="BIDs App to retrieve the haemodynamic response function from resting state fMRI data",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Madhur Tandon",
    author_email="madhurtandon23@gmail.com",
    url="https://github.com/BIDS-Apps/rsHRF",
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.5",
    install_requires=["numpy>=1.14,<1.15", "nibabel", "matplotlib", "scipy", "pybids", "pandas", "patsy", "duecredit",
                      "joblib"],
    cmdclass={
        'verify': VerifyVersionCommand,
    },
)
