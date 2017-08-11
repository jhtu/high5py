from collections import Iterable

import numpy as np
import h5py


# Check that a dataset exists
def exists(path_to_file, path_to_check_for):
    fid = h5py.File(path_to_file, 'r')
    available_paths = []
    fid.visit(available_paths.append)
    fid.close()
    return path_to_check_for in available_paths


# Load a dataset
def load_dataset(path_to_file, path_to_dataset):
    fid = h5py.File(path_to_file, 'r')
    path_to_dataset = unicode(path_to_dataset)
    data = fid[path_to_dataset][...]
    fid.close()
    return data


# Rename a dataset
def rename_dataset(
    path_to_file, old_path_to_dataset, new_path_to_dataset, new_desc=None):
    old_path_to_dataset = unicode(old_path_to_dataset)
    new_path_to_dataset = unicode(new_path_to_dataset)
    fid = h5py.File(path_to_file, 'a')
    fid[new_path_to_dataset] = fid[old_path_to_dataset]
    if new_desc is not None:
        fid[new_path_to_dataset].attrs['Description'] = new_desc
    del fid[old_path_to_dataset]
    fid.close()


# Save an array as a dataset.  If array is complex-valued, a group will be
# created containing the real and imaginary parts as separate datasets.
def save_array(path_to_file, array, name, desc, truncate=True):
    if truncate:
        file_mode = 'w'
    else:
        file_mode = 'a'
    name = unicode(name)
    fid = h5py.File(path_to_file, file_mode)
    if np.iscomplexobj(array):
        fid.create_group(name)
        fid[name].create_dataset('real', data=array.real)
        fid[name + '/real'].attrs['Description'] = 'Real part'
        fid[name].create_dataset('imag', data=array.imag)
        fid[name + '/imag'].attrs['Description'] = 'Imaginary part'
    else:
        fid.create_dataset(name, data=array)
    fid[name].attrs['Description'] = desc
    fid.close()


# Append an array as a dataset.
def append_array(path_to_file, array, name, desc):
    save_array(path_to_file, array, name, desc, truncate=False)


# Append scalars to a file.
def append_scalars(path_to_file, scalars, names, descs):
    if not isinstance(scalars, Iterable):
        scalars = [scalars]
        names = [names]
        descs = [descs]

    if not len(scalars) == len(names) == len(descs):
        raise ValueError(
            'Mismatch in number of scalars, names, and/or descs.')

    fid = h5py.File(path_to_file, 'a')
    for s, n, d in zip(scalars, names, descs):
        n = unicode(n)
        if np.iscomplexobj(s):
            fid.create_group(n)
            fid[n].create_dataset('real', data=s.real)
            fid[n + '/real'].attrs['Description'] = 'Real part'
            fid[n].create_dataset('imag', data=s.imag)
            fid[n + '/imag'].attrs['Description'] = 'Imaginary part'
        else:
            fid.create_dataset(n, data=s)
        fid[n].attrs['Description'] = d
    fid.close()
