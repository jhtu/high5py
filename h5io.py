import numpy as np
import h5py


# Get info about a group/dataset
def info(file_path, path='/'):
    path = '{}'.format(path)
    with h5py.File(file_path, 'r') as fid:
        info_dict = {'filename': fid.filename, 'name': fid[path].name}
        if isinstance(fid[path], h5py.Group):
            info_dict['groups'] = [
                subpath for subpath in fid[path]
                if isinstance(fid['{}/{}'.format(path, subpath)], h5py.Group)]
            info_dict['datasets'] = [
                subpath for subpath in fid[path]
                if isinstance(fid['{}/{}'.format(path, subpath)], h5py.Dataset)]
        if isinstance(fid[path], h5py.Dataset):
            info_dict['datatype'] = fid[path].dtype
            info_dict['shape'] = fid[path].shape
            info_dict['size'] = fid[path].size
            info_dict['chunks'] = fid[path].chunks
            info_dict['compression'] = fid[path].compression
        info_dict['attributes'] = [attr for attr in fid[path].attrs]
    for key, val in info_dict.items():
        print((
            '{:>' + '{:d}'.format(max([len(key) for key in info_dict.keys()])) +
            '}: {}').format(key, val))


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
def save_dataset(
    file_path, data, dataset_path='data', description=None, truncate=True):
    if truncate:
        file_mode = 'w'
    else:
        file_mode = 'a'
    dataset_path = u'{}'.format(dataset_path)
    with h5py.File(file_path, file_mode) as fid:
        fid.create_dataset(dataset_path, data=data)
        if description is not None:
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
def append_dataset(file_path, data, dataset_path, description=None):
    save_dataset(
        file_path, data, dataset_path, description=description, truncate=False)
