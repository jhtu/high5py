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

The documentation is available at https://high5py.readthedocs.io.

You can also build the documentation manually with Sphinx
(http://sphinx.pocoo.org).
From the ``high5py`` directory, run ``sphinx-build docs docs/_build`` and then open
``docs/_build/index.html`` in a web browser.
