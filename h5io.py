import numpy as np
import h5py


# Check that a dataset exists
def exists(file_path, target_dataset_path):
    avail_dataset_paths = []
    with h5py.File(file_path, 'r') as fid:
        fid.visit(avail_dataset_paths.append)
    return target_dataset_path in avail_dataset_paths


# Load a dataset
def load_dataset(file_path, dataset_path):
    dataset_path = u'{}'.format(dataset_path)
    with h5py.File(file_path, 'r') as fid:
        data = fid[dataset_path][()]
    return data


# Save a dataset
def save_dataset(file_path, data, dataset_path, description, truncate=True):
    if truncate:
        file_mode = 'w'
    else:
        file_mode = 'a'
    dataset_path = u'{}'.format(dataset_path)
    with h5py.File(file_path, file_mode) as fid:
        fid.create_dataset(dataset_path, data=data)
        fid[dataset_path].attrs['Description'] = description


# Rename a dataset
def rename_dataset(
        file_path, old_dataset_path, new_dataset_path, new_description=None):
    old_dataset_path = u'{}'.format(old_dataset_path)
    new_dataset_path = u'{}'.format(new_dataset_path)
    with h5py.File(file_path, 'a') as fid:
        fid[new_dataset_path] = fid[old_dataset_path]
        if new_description is not None:
            fid[new_dataset_path].attrs['Description'] = new_description
            del fid[old_dataset_path]


# Append a dataset
def append_dataset(file_path, data, dataset_path, description):
    save_array(file_path, data, dataset_path, description, truncate=False)
