from collections import Iterable

import numpy as np
import h5py


# Check that a dataset exists
def exists(path_to_file, path_to_check_for):
    available_paths = []
    with h5py.File(path_to_file, 'r') as fid:
        fid.visit(available_paths.append)
    return path_to_check_for in available_paths


# Load a dataset
def load_dataset(path_to_file, path_to_dataset):
    path_to_dataset = u'{}'.format(path_to_dataset)
    with h5py.File(path_to_file, 'r') as fid:
        data = fid[path_to_dataset][...]
    if len(data.shape) == 0:
        return np.asscalar(data)
    return data


# Rename a dataset
def rename_dataset(
    path_to_file, old_path_to_dataset, new_path_to_dataset, new_desc=None):
    old_path_to_dataset = u'{}'.format(old_path_to_dataset)
    new_path_to_dataset = u'{}'.format(new_path_to_dataset)
    with h5py.File(path_to_file, 'a') as fid:
        fid[new_path_to_dataset] = fid[old_path_to_dataset]
        if new_desc is not None:
            fid[new_path_to_dataset].attrs['Description'] = new_desc
        del fid[old_path_to_dataset]


# Save an array as a dataset.  If array is complex-valued, a group will be
# created containing the real and imaginary parts as separate datasets.
def save_array(path_to_file, array, name, desc, truncate=True):
    if truncate:
        file_mode = 'w'
    else:
        file_mode = 'a'
    name = u'{}'.format(name)
    with h5py.File(path_to_file, file_mode) as fid:
        fid.create_dataset(name, data=array)
        fid[name].attrs['Description'] = desc


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

    with h5py.File(path_to_file, 'a') as fid:
        for s, n, d in zip(scalars, names, descs):
            n = u'{}'.format(n)
            fid.create_dataset(n, data=s)
            fid[n].attrs['Description'] = d
