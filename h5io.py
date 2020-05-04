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


# Convert to NPZ (numpy archive) format
def to_npz(h5_file_path, npz_file_path, path='/'):

    with h5py.File(h5_file_path, 'r') as fid:

        # Gather dataset paths, looking for subpaths if the specified path
        # denotes a group
        if isinstance(path, str):
            path = u'{}'.format(path)
            if isinstance(fid[path], h5py.Dataset):
                subpaths = [path]
            elif isinstance(fid[path], h5py.Group):
                subpaths = ['{}/{}'.format(path, sp) for sp in fid[path]]
            else:
                raise ValueError('Unrecognized h5py type.')
        # Otherwise assume that the specified path is a container of subpaths
        else:
            subpaths = [fid[sp].name for sp in path]

        # Check that each subpath corresponds to a dataset, not a group, as it
        # is unclear how to save subgroups (which may be further nested)
        if any([not isinstance(fid[sp], h5py.Dataset) for sp in subpaths]):
            raise ValueError('Specified path contains groups.')

        # Gather data for saving. Process subpath names, ignoring the slash
        # corresponding to root, and replacing all further slashes with
        # underscores
        kwargs = {}
        for sp in subpaths:
            name = sp.split('/')[-1]
            kwargs[name] = fid[sp][()]

        # Save data
        np.savez_compressed(npz_file_path, **kwargs)
