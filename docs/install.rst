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
