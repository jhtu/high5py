Installation
============

The easiest way to install ``high5py`` is using pip::

  pip install high5py

To install from source, download the source code from Github::

  git clone git://github.com:jhtu/high5py.git

Next, navigate to the directory containing the source code, then build and install the package::

  python setup.py build
  python setup.py install

To be sure the code is working, run the unit tests::

  python -c 'import high5py as hi5; hi5.run_all_tests()'
