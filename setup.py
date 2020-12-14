import os
from setuptools import setup, find_packages
from pkg_resources import parse_version


# Locate current location
here = os.path.abspath(os.path.dirname(__file__))

# Get the version from the relevant file
with open(os.path.join(os.path.join(here, 'high5py'), '_version.py')) as f:
    exec(f.read())

# Get the development status from the version string
parsed_version = str(parse_version(__version__))
if any(w in ['*a', '*alpha'] for w in parsed_version):
    devstatus = 'Development Status :: 3 - Alpha'
elif any(w in ['*b', '*beta'] for w in parsed_version):
    devstatus = 'Development Status :: 4 - Beta'
else:
    devstatus = 'Development Status :: 5 - Production/Stable'

# Setup
setup(
    name='high5py',
    version=__version__,
    description='Interact with HDF5 files using one-line function calls.',
    author='Jonathan Tu',
    url='http://high5py.readthedocs.io',
    maintainer='Jonathan Tu',
    license='Free BSD',
    classifiers=[
        # How mature is this project? Common values are
        # 3 - Alpha
        # 4 - Beta
        # 5 - Production/Stable
        devstatus,
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],
    packages=['high5py'],
    package_dir={'high5py': 'high5py'},
    install_requires=['h5py', 'numpy']
)
