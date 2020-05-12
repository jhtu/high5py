import numpy as _np
import h5py as _h5py


def info(file_path, path='/', return_info=False):
    """Print and return information about HDF5 file, group, or dataset.

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    path: str, optional
        HDF5 path to group or dataset.  Defaults to root group ('/').

    Returns
    -------
    dict, optional
        Dictionary of key, value pairs describing specified group or dataset.
        Only provided if return_info is True.
    """
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
        info_dict['attributes'] = {
            key: val for key, val in fid[path].attrs.items()}
    for key, val in info_dict.items():
        print((
            '{:>' + '{:d}'.format(max([len(key) for key in info_dict.keys()]))
            + '}: {}').format(key, val))
    if return_info:
        return info_dict


def exists(file_path, path):
    """Determine if path exists in HDF5 file.

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    path: str
        HDF5 path to group or dataset.

    Returns
    -------
    bool
        Boolean describing if path exists in HDF5 file.
    """
    avail_paths = []
    with _h5py.File(file_path, 'r') as fid:
        fid.visit(avail_paths.append)
    return path in avail_paths


def load_dataset(file_path, path):
    """Load dataset from HDF5 file.

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    path: str
        HDF5 path to dataset.

    Returns
    -------
    array-like, scalar, or str
        Dataset values will be returned with same type they were saved (usually
        some sort of numpy array), except that single-element arrays will be
        returned as scalars.
    """
    with _h5py.File(file_path, 'r') as fid:
        data = fid[path][()]
    return data


def save_dataset(
    file_path, data, path='data', description=None, overwrite=True):
    """Save dataset to HDF5 file (overwrites file by default).

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    data: array-like, scalar, or str
        Data to save.
    path: str, optional
        HDF5 path to dataset.  Can be a multi-level path denoting a dataset
        within a group, such as '/group/dataset'.  Defaults to 'data'.
    description: str, optional
        String describing dataset.  Description is saved as an HDF5 attribute of
        the dataset.  Defaults to None, for which no description is saved.
    overwrite: bool
        If True, saving overwrites the file.  Otherwise, data is appended to the
        file.  Defaults to True.
    """
    if overwrite:
        file_mode = 'w'
    else:
        file_mode = 'a'
    with _h5py.File(file_path, file_mode) as fid:
        fid.create_dataset(path, data=data)
        if description is not None:
            fid[path].attrs['Description'] = description


def rename_dataset(file_path, old_path, new_path, new_description=None):
    """Rename group or dataset in HDF5 file.

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    old_path: str
        Old path to HDF5 group or dataset.
    new_path: str
        New path to HDF5 group or dataset.
    description: str, optional
        New string describing dataset.  Description is saved as an HDF5
        attribute of the dataset.  Defaults to None, for which the old
        description is kept.
    """
    with _h5py.File(file_path, 'a') as fid:
        fid[new_path] = fid[old_path]
        if new_description is not None:
            fid[new_path].attrs['Description'] = new_description
        del fid[old_path]


def append_dataset(file_path, data, path='data', description=None):
    """Append dataset to HDF5 file (never overwrites file).

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    data: array-like, scalar, or str
        Data to save.
    path: str, optional
        HDF5 path to dataset.  Can be a multi-level path denoting a dataset
        within a group, such as '/group/dataset'.  Defaults to 'data'.
    description: str, optional
        String describing dataset.  Description is saved as an HDF5 attribute of
        the dataset.  Defaults to None, for which no description is saved.
    """
    save_dataset(
        file_path, data, path=path, description=description, overwrite=False)


def to_npz(h5_file_path, npz_file_path, path='/'):
    """Save an HDF5 group or dataset to NPZ (compressed numpy archive) format.
    Subgroups such as path/group/subgroup/dataset will be saved with array names
    path_group_subgroup_dataset.

    Parameters
    ----------
    h5_file_path: str
        Path to HDF5 file.
    npz_file_path: str
        Path to NPZ file.
    path: str, optional
        HDF5 path to group or dataset to save.  Can be a multi-level path
        denoting a dataset within a group, such as '/group/dataset'.  Defaults
        to root group ('/').
    """
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
    """Load data from an NPZ (compressed numpy archive) file and save to HDF5.
    NPZ array names are preserved.

    Parameters
    ----------
    npz_file_path: str
        Path to NPZ file.
    h5_file_path: str
        Path to HDF5 file.
    """
    # Open file for processing
    with _np.load(npz_file_path) as data:

        # Loop through arrays
        for idx, (key, val) in enumerate(data.items()):

            # Save to HDF5
            if idx == 0:
                save_dataset(h5_file_path, val, path=key)
            else:
                append_dataset(h5_file_path, val, path=key)
