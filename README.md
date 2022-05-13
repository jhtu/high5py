# Welcome

`high5py` is a high-level interface to `h5py`, which is itself a high-level interface to the HDF5 library.
You can use `high5py` to make one-line calls for the most common HDF5 tasks, like saving and loading data.
For example:
```
import numpy as np
import high5py as hi5

hi5.save_dataset('data.h5', np.random.rand(100), name='x')
x = hi5.load_dataset('data.h5', name='x')
```


# Installation

## From PyPI

The easiest way to install `high5py` is using pip (and PyPI):
```
pip install high5py
```

## From source

To install from source, download the source code from Github:
```
# Using SSH
git clone git://github.com:jhtu/high5py.git

# Using HTTPS
git clone https://github.com/jhtu/high5py.git
```
Next, navigate to the `high5py` root directory (the one containing `setup.py`).  Then run
```
pip install .
```

## Testing the code

To be sure the code is working, run the unit tests:
```
python -c 'import high5py as hi5; hi5.run_all_tests()'
```


# Documentation

A tutorial notebook is available in the source code at [`examples/tutorial.ipynb`](https://github.com/jhtu/high5py/blob/master/examples/tutorial.ipynb).
The full documentation is available at [ReadTheDocs](https://high5py.readthedocs.io).
You can also build it manually with [Sphinx](http://sphinx.pocoo.org).
To do so, navigate to the `high5py` root directory (the one containing `setup.py`).
Then run
```
sphinx-build docs docs/_build
```
You can then open `docs/_build/index.html` in a web browser.


# Licensing

`high5py` is published under the BSD 3-clause license.
The license file is available [here](https://github.com/jhtu/high5py/blob/master/LICENSE.txt).
