import numpy as _np
import h5py as _h5py


def info(file_path, name='/', return_info=False):
    """Print and return information about HDF5 file/group/dataset.

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    name: str, optional
        HDF5 group/dataset name (e.g., /group/dataset).  Defaults to root group
        ('/').

    Returns
    -------
    info: dict, optional
        Dictionary of key, value pairs describing specified file/group/dataset.
        Only provided if return_info is True.
    """
    name = '{}'.format(name)
    with _h5py.File(file_path, 'r') as fid:
        info_dict = {'filename': fid.filename, 'name': fid[name].name}
        if isinstance(fid[name], _h5py.Group):
            info_dict['groups'] = [
                subname for subname in fid[name]
                if isinstance(fid['{}/{}'.format(name, subname)], _h5py.Group)]
            info_dict['datasets'] = [
                subname for subname in fid[name]
                if isinstance(
                    fid['{}/{}'.format(name, subname)],_h5py.Dataset)]
        if isinstance(fid[name], _h5py.Dataset):
            info_dict['datatype'] = fid[name].dtype
            info_dict['shape'] = fid[name].shape
            info_dict['size'] = fid[name].size
            info_dict['chunks'] = fid[name].chunks
            info_dict['compression'] = fid[name].compression
        info_dict['attributes'] = {
            key: val for key, val in fid[name].attrs.items()}
    for key, val in info_dict.items():
        print((
            '{:>' + '{:d}'.format(max([len(key) for key in info_dict.keys()]))
            + '}: {}').format(key, val))
    if return_info:
        return info_dict


def exists(file_path, name):
    """Determine if group/dataset name exists in HDF5 file.

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    name: str
        HDF5 group/dataset name (e.g., /group/dataset).

    Returns
    -------
    exists: bool
        Boolean describing if path exists in HDF5 file.
    """
    avail_names = []
    with _h5py.File(file_path, 'r') as fid:
        fid.visit(avail_names.append)
    return name in avail_names


def load_dataset(file_path, name):
    """Load dataset from HDF5 file.

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    name: str
        HDF5 dataset name (e.g., /group/dataset).

    Returns
    -------
    data: array-like, scalar, or str
        Dataset values will be returned with same type they were saved (usually
        some sort of numpy array), except that single-element arrays will be
        returned as scalars.
    """
    with _h5py.File(file_path, 'r') as fid:
        data = fid[name][()]
    return data


def save_dataset(
    file_path, data, name='data', description=None, overwrite=True):
    """Save dataset to HDF5 file (overwrites file by default).

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    data: array-like, scalar, or str
        Data to save.
    name: str, optional
        HDF5 dataset name (e.g., /group/dataset).  Defaults to 'data'.
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
        fid.create_dataset(name, data=data)
        if description is not None:
            fid[name].attrs['Description'] = description


def rename(file_path, old_name, new_name, new_description=None):
    """Rename group/dataset in HDF5 file.

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    old_name: str
        Old HDF5 name (e.g., /group/old_dataset).
    new_name: str
        New HDF5 name (e.g., /group/new_dataset).
    description: str, optional
        New string describing dataset.  Description is saved as an HDF5
        attribute of the dataset.  Defaults to None, for which the old
        description is kept.
    """
    with _h5py.File(file_path, 'a') as fid:
        fid[new_name] = fid[old_name]
        if new_description is not None:
            fid[new_name].attrs['Description'] = new_description
        del fid[old_name]


def append_dataset(file_path, data, name='data', description=None):
    """Append dataset to HDF5 file (never overwrites file).

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    data: array-like, scalar, or str
        Data to save.
    name: str, optional
        HDF5 dataset name (e.g., /group/dataset).  Defaults to 'data'.
    description: str, optional
        String describing dataset.  Description is saved as an HDF5 attribute of
        the dataset.  Defaults to None, for which no description is saved.
    """
    save_dataset(
        file_path, data, name=name, description=description, overwrite=False)


def save_attributes(file_path, attributes, name='data', overwrite=True):
    """Save HDF5 group/dataset attributes (overwrites existing attributes by
    default).

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    attributes: dict
        Attributes to save.
    name: str, optional
        HDF5 group/dataset name (e.g., /group/dataset).  Defaults to 'data'.
    overwrite: bool
        If True, saving overwrites existing attributes.  Otherwise, new
        attributes are appended to existing ones.  Defaults to True.
    """
    with _h5py.File(file_path, 'a') as fid:
        if overwrite:
            for key, val in fid[name].attrs.items():
                del fid[name].attrs[key]
        for key, val in attributes.items():
            fid[name].attrs[key] = val


def append_attributes(file_path, attributes, name='data'):
    """Append HDF5 group/dataset attributes (never overwrites existing
    attributes).

    Parameters
    ----------
    file_path: str
        Path to HDF5 file.
    attributes: dict
        Attributes to append.
    name: str, optional
        HDF5 group/dataset name (e.g., /group/dataset).  Defaults to 'data'.
    """
    save_attributes(file_path, attributes, name=name, overwrite=False)


def to_npz(h5_file_path, npz_file_path, name='/'):
    """Save an HDF5 group/dataset to NPZ (compressed numpy archive) format.
    Subgroups such as path/group/subgroup/dataset will be saved with array names
    such as path_group_subgroup_dataset.

    Parameters
    ----------
    h5_file_path: str
        Path to HDF5 file.
    npz_file_path: str
        Path to NPZ file.
    name: str, optional
        HDF5 group/dataset name (e.g., /group/dataset).  Defaults to root group
        ('/').
    """
    # Open file for processing
    with _h5py.File(h5_file_path, 'r') as fid:

        # Initialize root, paths to check
        dataset_names = []
        if isinstance(name, str):
            if isinstance(fid[name], _h5py.Dataset):
                root = '/'
                dataset_names = [fid[name].name]
                names_to_check = []
            else:
                root = name
                names_to_check = [name]
        else:
            root = '/'
            names_to_check = name

        # Process until there are no more paths to check
        while len(names_to_check) > 0:
            for subname in names_to_check:
                if isinstance(fid[subname], _h5py.Dataset):
                    dataset_names.append(fid[subname].name)
                    names_to_check.remove(subname)
                elif isinstance(fid[subname], _h5py.Group):
                    for subsubname in fid[subname]:
                        names_to_check.append(
                            fid['{}/{}'.format(subname, subsubname)].name)
                    names_to_check.remove(subname)

        # Generate dataset names for NPZ file starting from the specified root,
        # and replacing slashes with underscores, since NPZ files don't have
        # groups
        kwargs = {}
        for dsn in dataset_names:

            # Split off first instance of root
            key = root.join(dsn.split(root)[1:])

            # Remove leading slash, if any
            if key[0] == '/':
                key = key[1:]

            # Replace slashes with underscores
            key = key.replace('/', '_')

            # Add processed name
            kwargs[key] = fid[dsn][()]

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
                save_dataset(h5_file_path, val, name=key)
            else:
                append_dataset(h5_file_path, val, name=key)
