# Set up top level namespace
from ._version import __version__
from .high5py import *
from .testhigh5py import run_all_tests


# This must be defined for the Sphinx autodocumentation to work
__all__ = [
    'info',
    'list_all',
    'exists',
    'load_dataset',
    'save_dataset',
    'delete',
    'rename',
    'append_dataset',
    'replace_dataset',
    'load_attributes',
    'save_attributes',
    'append_attributes',
    'to_npz',
    'from_npz'
]
