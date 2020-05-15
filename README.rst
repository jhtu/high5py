Welcome
=======

``h5io`` is a high-level interface to ``h5py``, which is itself a high-level interface to the HDF5 library.
You can use ``h5io`` to make one-line calls for the most common HDF5 tasks, like saving and loading data.


Installation
============

To run ``h5io``, first download the source code from Github::

  git clone git://github.com:jhtu/h5io.git

Next, navigate to the directory containing the source code, then build and install the package::

  python setup.py build
  python setup.py install

To be sure the code is working, run the unit tests::

  python -c 'import h5io; h5io.run_all_tests()'

The documentation is available at https://h5io.readthedocs.io.

You can also build the documentation manually with Sphinx
(http://sphinx.pocoo.org).
From the ``h5io`` directory, run ``sphinx-build docs docs/build`` and then open
``docs/build/index.html`` in a web browser.


Tutorial
========

A tutorial is provided as a Juptyer notebook (``tutorial.ipynb``), as well as in the online documentation at https://h5io.readthedocs.io.


Dependencies
============

``h5io`` requires ``numpy`` and ``h5py``.
