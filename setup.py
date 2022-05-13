import os
from setuptools import setup
import sys


# Locate version module and import
pkg_name = 'high5py'
curr_dir = os.path.abspath(os.path.dirname(__file__))
version_dir = os.path.join(curr_dir, pkg_name)
sys.path.append(version_dir)
from _version import __version__

# Setup
setup(
    name='high5py',
    version=__version__,
    description='Interact with HDF5 files using one-line function calls',
    author='Jonathan H. Tu',
    url='http://high5py.readthedocs.io',
    maintainer='Jonathan H. Tu',
    license='Free BSD',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
    packages=[pkg_name],
    install_requires=['h5py', 'numpy']
)
