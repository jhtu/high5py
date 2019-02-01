# Setup top level namespace
from .h5io import exists, load_dataset, rename_dataset, save_array,\
    append_array, append_scalars
from .alltests import run_all_tests
from . import testh5io
