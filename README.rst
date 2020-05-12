This library contains a set of functions for writing data to/reading data from
HDF5 files.  They are implemented on an even higher-level than h5py functions,
requiring the user to know very little about the HDF5 format to use them.

To use this library, simply add the parent directory to your PYTHONPATH, or install the source code using:
    python setup.py build
    python setup.py install

To check that the library is working properly, run the tests:
    python -c "import h5io; h5io.run_all_tests()"
