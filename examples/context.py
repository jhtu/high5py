import os
import sys


# Locate dasp modules
curr_dir = os.path.dirname(__file__)
pkg_dir = os.path.abspath(os.path.join(curr_dir, '..'))
sys.path.insert(0, pkg_dir)

# Import torchhelper module
import high5py
