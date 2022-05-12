import numpy as _np
import h5py as _h5py


def info(filepath, name='/', return_info=False):
    """Print and return information about HDF5 file/group/dataset.

    Parameters
    ----------
    filepath: str
        Path to HDF5 file.
    name: str, optional
        HDF5 group/dataset name (e.g., /group/dataset).  Defaults to root group
        ('/').
    return_info: bool, optional
        If True, return a dictionary of results.  Defaults to False.

    Returns
    -------
    info: dict, optional
        Dictionary of key, value pairs describing specified file/group/dataset.
        Only provided if return_info is True.
    """
    name = '{}'.format(name)
    with _h5py.File(filepath, 'r') as fid:
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


def list_all(filepath, name='/', return_info=False):
    """List all groups and datasets in HDF5 file or group.

    Parameters
    ----------
    filepath: str
        Path to HDF5 file.
    name: str, optional
        HDF5 group name (e.g., /group).  Defaults to root group ('/').
    return_into: bool, optional
        If True, return a dictionary of results.  Defaults to False.

    Returns
    -------
    info: dict, optional
        Dictionary of key, value pairs describing specified file/group.  Only
        provided if return_info is True.
    """
    all_names = []
    all_items = {}
    with _h5py.File(filepath, 'r') as fid:
        fid[name].visit(all_names.append)
        max_len = max([len(name) for name in all_names])
        def print_item(name, obj):
            all_items[name] = str(obj)
            print(
                ('{:<' + '{:d}'.format(max_len) + '}    {}').format(name, obj))
        fid[name].visititems(print_item)
    if return_info:
        return all_items


def exists(filepath, name):
    """Determine if group/dataset name exists in HDF5 file.

    Parameters
    ----------
    filepath: str
        Path to HDF5 file.
    name: str
        HDF5 group/dataset name (e.g., /group/dataset).

    Returns
    -------
    exists: bool
        Boolean describing if path exists in HDF5 file.
    """
    avail_names = []
    with _h5py.File(filepath, 'r') as fid:
        fid.visit(avail_names.append)
    return name in avail_names


def load_dataset(filepath, name='data', start_index=None, end_index=None):
    """Load dataset from HDF5 file.

    Parameters
    ----------
    filepath: str
        Path to HDF5 file.
    name: str, optional
        HDF5 dataset name (e.g., /group/dataset).  Defaults to 'data'.
    start_index: int, optional
        Start index for slicing HDF5 dataset.  Providing a slice index here may
        be more efficient than returning the entire dataset and then slicing.
        Defaults to None, for which no slicing will be done on the beginning of
        the dataset.
    end_index: int, optional
        End index for slicing HDF5 dataset.  Providing a slice index here may be
        more efficient than returning the entire dataset and then slicing.
        Defaults to None, for which no slicing will be done on the end of the
        dataset.

    Returns
    -------
    data: array-like, scalar, or str
        Dataset values will be returned with same type they were saved (usually
        some sort of numpy array), except that single-element arrays will be
        returned as scalars.
    """
    with _h5py.File(filepath, 'r') as fid:
        if start_index is None and end_index is None:
            data = fid[name][()]
        elif start_index is None and end_index is not None:
            data = fid[name][:end_index]
        elif start_index is not None and end_index is None:
            data = fid[name][start_index:]
        else:
            data = fid[name][start_index:end_index]
    return data


def save_dataset(
    filepath, data, name='data', description=None, overwrite=True,
    compression_level=None):
    """Save dataset to HDF5 file (overwrites file by default).

    Parameters
    ----------
    filepath: str
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
    compression_level: int or None, optional
        Integer from 0 to 9 specifying compression level for gzip filter, which
        is available on all h5py installations and offers good compression with
        moderate speed.  Defaults to None, for which no compression/filter is
        applied.
    """
    if overwrite:
        file_mode = 'w'
    else:
        file_mode = 'a'
    with _h5py.File(filepath, file_mode) as fid:
        if compression_level is not None:
            fid.create_dataset(
                name, data=data, compression='gzip',
                compression_opts=compression_level)
        else:
            fid.create_dataset(name, data=data)
        if description is not None:
            fid[name].attrs['Description'] = description


def delete(filepath, name):
    """Delete group/dataset in HDF5 file.

    Parameters
    ----------
    filepath: str
        Path to HDF5 file.
    name: str
        HDF5 name (e.g., /group/old_dataset).
    """
    with _h5py.File(filepath, 'a') as fid:
        del fid[name]


def rename(filepath, old_name, new_name, new_description=None):
    """Rename group/dataset in HDF5 file.

    Parameters
    ----------
    filepath: str
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
    with _h5py.File(filepath, 'a') as fid:
        fid[new_name] = fid[old_name]
        if new_description is not None:
            fid[new_name].attrs['Description'] = new_description
        del fid[old_name]


def append_dataset(
    filepath, data, name='data', description=None, compression_level=None):
    """Append dataset to HDF5 file (never overwrites file).

    Parameters
    ----------
    filepath: str
        Path to HDF5 file.
    data: array-like, scalar, or str
        Data to save.
    name: str, optional
        HDF5 dataset name (e.g., /group/dataset).  Defaults to 'data'.
    description: str, optional
        String describing dataset.  Description is saved as an HDF5 attribute of
        the dataset.  Defaults to None, for which no description is saved.
    compression_level: int or None, optional
        Integer from 0 to 9 specifying compression level for gzip filter, which
        is available on all h5py installations and offers good compression with
        moderate speed.  Defaults to None, for which no compression/filter is
        applied.
    """
    save_dataset(
        filepath, data, name=name, description=description, overwrite=False,
        compression_level=compression_level)


def replace_dataset(
    filepath, data, name='data', description=None, compression_level=None):
    """Replace/overwrite a dataset in an HDF5 file (do not overwrite the whole
    file).

    Parameters
    ----------
    filepath: str
        Path to HDF5 file.
    data: array-like, scalar, or str
        Data to save.
    name: str, optional
        HDF5 dataset name (e.g., /group/dataset).  Defaults to 'data'.
    description: str, optional
        String describing dataset.  Description is saved as an HDF5 attribute of
        the dataset.  Defaults to None, for which no description is saved.
    compression_level: int or None, optional
        Integer from 0 to 9 specifying compression level for gzip filter, which
        is available on all h5py installations and offers good compression with
        moderate speed.  Defaults to None, for which no compression/filter is
        applied.
    """
    delete(filepath, name)
    append_dataset(
        filepath, data, name=name, description=description,
        compression_level=compression_level)


def load_attributes(filepath, name='data'):
    """Load HDF5 group/dataset attributes from HDF5 file.

    Parameters
    ----------
    filepath: str
        Path to HDF5 file.
    name: str, optional
        HDF5 dataset name (e.g., /group/dataset).  Defaults to 'data'.

    Returns
    -------
    attributes: dict
        Dictionary of loaded attributes.
    """
    with _h5py.File(filepath, 'r') as fid:
        return dict(fid[name].attrs)


def save_attributes(filepath, attributes, name='data', overwrite=True):
    """Save HDF5 group/dataset attributes (overwrites existing attributes by
    default).

    Parameters
    ----------
    filepath: str
        Path to HDF5 file.
    attributes: dict
        Attributes to save.
    name: str, optional
        HDF5 group/dataset name (e.g., /group/dataset).  Defaults to 'data'.
    overwrite: bool
        If True, saving overwrites existing attributes.  Otherwise, new
        attributes are appended to existing ones.  Defaults to True.
    """
    with _h5py.File(filepath, 'a') as fid:
        if overwrite:
            for key, val in fid[name].attrs.items():
                del fid[name].attrs[key]
        for key, val in attributes.items():
            fid[name].attrs[key] = val


def append_attributes(filepath, attributes, name='data'):
    """Append HDF5 group/dataset attributes (never overwrites existing
    attributes).

    Parameters
    ----------
    filepath: str
        Path to HDF5 file.
    attributes: dict
        Attributes to append.
    name: str, optional
        HDF5 group/dataset name (e.g., /group/dataset).  Defaults to 'data'.
    """
    save_attributes(filepath, attributes, name=name, overwrite=False)


def to_npz(h5_filepath, npz_filepath, name='/'):
    """Save an HDF5 group/dataset to NPZ (compressed numpy archive) format.
    Subgroups such as path/group/subgroup/dataset will be saved with array names
    such as path_group_subgroup_dataset.

    Parameters
    ----------
    h5_filepath: str
        Path to HDF5 file.
    npz_filepath: str
        Path to NPZ file.
    name: str, optional
        HDF5 group/dataset name (e.g., /group/dataset).  Defaults to root group
        ('/').
    """
    # Open file for processing
    with _h5py.File(h5_filepath, 'r') as fid:

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
    _np.savez_compressed(npz_filepath, **kwargs)


# Convert from NPZ (numpy archive) format
def from_npz(npz_filepath, h5_filepath):
    """Load data from an NPZ (compressed numpy archive) file and save to HDF5.
    NPZ array names are preserved.

    Parameters
    ----------
    npz_filepath: str
        Path to NPZ file.
    h5_filepath: str
        Path to HDF5 file.
    """
    # Open file for processing
    with _np.load(npz_filepath) as data:

        # Loop through arrays
        for idx, (key, val) in enumerate(data.items()):

            # Save to HDF5
            if idx == 0:
                save_dataset(h5_filepath, val, name=key)
            else:
                append_dataset(h5_filepath, val, name=key)
