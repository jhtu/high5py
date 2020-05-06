import numpy as _np
import h5py as _h5py


# Get info about a group/dataset
def info(file_path, path='/'):
    path = '{}'.format(path)
    with _h5py.File(file_path, 'r') as fid:
        info_dict = {'filename': fid.filename, 'name': fid[path].name}
        if isinstance(fid[path], _h5py.Group):
            info_dict['groups'] = [
                subpath for subpath in fid[path]
                if isinstance(fid['{}/{}'.format(path, subpath)], _h5py.Group)]
            info_dict['datasets'] = [
                subpath for subpath in fid[path]
                if isinstance(
                    fid['{}/{}'.format(path, subpath)],_h5py.Dataset)]
        if isinstance(fid[path], _h5py.Dataset):
            info_dict['datatype'] = fid[path].dtype
            info_dict['shape'] = fid[path].shape
            info_dict['size'] = fid[path].size
            info_dict['chunks'] = fid[path].chunks
            info_dict['compression'] = fid[path].compression
        info_dict['attributes'] = [attr for attr in fid[path].attrs]
    for key, val in info_dict.items():
        print((
            '{:>' + '{:d}'.format(max([len(key) for key in info_dict.keys()]))
            + '}: {}').format(key, val))
    return info_dict


# Check that a dataset exists
def exists(file_path, target_path):
    avail_paths = []
    with _h5py.File(file_path, 'r') as fid:
        fid.visit(avail_paths.append)
    return target_path in avail_paths


# Load a dataset
def load_dataset(file_path, dataset_path):
    with _h5py.File(file_path, 'r') as fid:
        data = fid[dataset_path][()]
    return data


# Save a dataset
def save_dataset(
    file_path, data, dataset_path='data', description=None, truncate=True):
    if truncate:
        file_mode = 'w'
    else:
        file_mode = 'a'
    with _h5py.File(file_path, file_mode) as fid:
        fid.create_dataset(dataset_path, data=data)
        if description is not None:
            fid[dataset_path].attrs['Description'] = description


# Rename a dataset
def rename_dataset(
    file_path, old_dataset_path, new_dataset_path, new_description=None):
    with _h5py.File(file_path, 'a') as fid:
        fid[new_dataset_path] = fid[old_dataset_path]
        if new_description is not None:
            fid[new_dataset_path].attrs['Description'] = new_description
        del fid[old_dataset_path]


# Append a dataset
def append_dataset(file_path, data, dataset_path='data', description=None):
    save_dataset(
        file_path, data, dataset_path=dataset_path, description=description,
        truncate=False)


# Convert to NPZ (numpy archive) format
def to_npz(h5_file_path, npz_file_path, path='/'):

    # Open file for processing
    with _h5py.File(h5_file_path, 'r') as fid:

        # Initialize root, paths to check
        dataset_paths = []
        if isinstance(path, str):
            if isinstance(fid[path], _h5py.Dataset):
                root = '/'
                dataset_paths = [fid[path].name]
                paths_to_check = []
            else:
                root = path
                paths_to_check = [path]
        else:
            root = '/'
            paths_to_check = path

        # Process until there are no more paths to check
        while len(paths_to_check) > 0:
            for subpath in paths_to_check:
                if isinstance(fid[subpath], _h5py.Dataset):
                    dataset_paths.append(fid[subpath].name)
                    paths_to_check.remove(subpath)
                elif isinstance(fid[subpath], _h5py.Group):
                    for subsubpath in fid[subpath]:
                        paths_to_check.append(
                            fid['{}/{}'.format(subpath, subsubpath)].name)
                    paths_to_check.remove(subpath)

        # Generate dataset names for NPZ file starting from the specified root,
        # and replacing slashes with underscores, since NPZ files don't have
        # groups
        kwargs = {}
        for dsp in dataset_paths:

            # Split off first instance of root
            key = root.join(dsp.split(root)[1:])

            # Remove leading slash, if any
            if key[0] == '/':
                key = key[1:]

            # Replace slashes with underscores
            key = key.replace('/', '_')

            # Add processed name
            kwargs[key] = fid[dsp][()]

    # Save data
    _np.savez_compressed(npz_file_path, **kwargs)


# Convert from NPZ (numpy archive) format
def from_npz(npz_file_path, h5_file_path):

    # Open file for processing
    with _np.load(npz_file_path) as data:

        # Loop through arrays
        for idx, (key, val) in enumerate(data.items()):

            # Save to HDF5
            if idx == 0:
                save_dataset(h5_file_path, val, dataset_path=key)
            else:
                append_dataset(h5_file_path, val, dataset_path=key)
