import unittest as _unittest
import os as _os
import shutil as _shutil

import numpy as _np
import h5py as _h5py
import high5py as _hi5


def run_all_tests():
    test_loader = _unittest.defaultTestLoader
    test_suites = test_loader.discover(_os.path.dirname(__file__))
    _unittest.TextTestRunner(buffer=True).run(test_suites)


class TestHigh5Py(_unittest.TestCase):
    def setUp(self):
        self.outdir = _os.path.join(_os.path.dirname(__file__), 'tmp/')
        self.filepath = self.outdir + 'test_file.py'
        if not _os.path.isdir(self.outdir):
            _os.mkdir(self.outdir)
        self.generate_data()


    def tearDown(self):
        _shutil.rmtree(self.outdir, ignore_errors=True)


    def generate_data(self):
        # Types of data to create
        self.dtype_names = ['int', 'float', 'complex']
        self.array_types = ['scalar', 'vector', 'array']
        self.dset_names = ['%s/%s' % (d_type, a_type)
            for d_type in self.dtype_names for a_type in self.array_types]
        self.var_names = [name.replace('/', '_') for name in self.dset_names]
        self.num_rows = _np.random.randint(2, 10)
        self.num_cols = _np.random.randint(2, 10)

        # Make some scalar data (create an array first, so that the type is
        # _np.int32, not int, for later comparisons)
        self.int_scalar = _np.array(_np.random.randint(-10, 10))[()]
        self.float_scalar = _np.array(_np.random.rand())[()]
        self.complex_scalar = _np.array(
            _np.random.rand() + 1j * _np.random.rand())[()]

        # Make some vector data
        self.int_vector = _np.random.randint(-10, 10, size=self.num_rows)
        self.float_vector = _np.random.rand(self.num_rows)
        self.complex_vector = (
            _np.random.rand(self.num_rows) +
            1j * _np.random.rand(self.num_rows))

        # Make some array data
        self.int_array = _np.random.randint(
            -10, 10, size=(self.num_rows, self.num_cols))
        self.float_array = _np.random.rand(self.num_rows, self.num_cols)
        self.complex_array = (
            _np.random.rand(self.num_rows, self.num_cols) +
            1j * _np.random.rand(self.num_rows, self.num_cols))

        # Save to HDF5 file
        with _h5py.File(self.filepath, 'w') as fid:
            for dset_name, var_name in zip(self.dset_names, self.var_names):
                fid[dset_name] = getattr(self, var_name)


    # Check equality for both arrays and scalars
    def _helper_assert_equal(self, test_data, true_data):
        self.assertEqual(type(test_data), type(true_data))
        if isinstance(true_data, _np.ndarray):
            _np.testing.assert_array_equal(test_data, true_data)
        else:
            self.assertEqual(test_data, true_data)


    # Check that a dataset inside an HDF5 file is correct
    def _helper_check_dataset(self, filepath, dset_name, true_data, desc):

        # Split dataset name into group and dataset parts
        grp, dset = dset_name.split('/')

        # Open file
        with _h5py.File(filepath, 'r') as fid:

            # Check that group exists
            self.assertTrue(grp in list(fid))

            # Check that dataset exists
            self.assertTrue(dset in list(fid[grp]))

            # Check description of dataset
            self.assertEqual(
                fid['{}/{}'.format(grp, dset)].attrs['Description'], desc)

            # Check values
            saved_data = fid['{}/{}'.format(grp, dset)][()]
            self._helper_assert_equal(saved_data, true_data)


    # Check that existence of groups/datasets can be queried correctly
    def test_exists(self):
        with _h5py.File(self.filepath, 'w') as fid:
            fid['existing/dataset'] = 'data_string'
        self.assertTrue(_hi5.exists(self.filepath, 'existing'))
        self.assertTrue(_hi5.exists(self.filepath, 'existing/dataset'))
        self.assertFalse(_hi5.exists(self.filepath, 'existing/other'))
        self.assertFalse(_hi5.exists(self.filepath, 'nonexistent/dataset'))


    # Check that datasets can be loaded correctly
    def test_load_dataset(self):
        for dset_name, var_name in zip(self.dset_names, self.var_names):
            loaded_data = _hi5.load_dataset(self.filepath, dset_name)
            true_data = getattr(self, var_name)
            self._helper_assert_equal(loaded_data, true_data)


    # Check that datasets can be saved correctly, with and without compression
    def test_save_dataset(self):
        for dset_name, var_name in zip(self.dset_names, self.var_names):
            for comp_lvl in [None, 4, 9]:
                true_data = getattr(self, var_name)
                filepath = self.outdir + var_name + '_saved.h5'
                desc = dset_name + ' description'
                with _h5py.File(filepath, 'w') as fid:
                    fid['old_data'] = 'old_data'
                if 'scalar' in dset_name:
                    _hi5.save_dataset(
                        filepath, true_data, name=dset_name, description=desc)
                else:
                    _hi5.save_dataset(
                        filepath, true_data, name=dset_name, description=desc,
                        compression_level=comp_lvl)
                self._helper_check_dataset(filepath, dset_name, true_data, desc)
                with _h5py.File(filepath, 'r') as fid:
                    self.assertFalse('old_data' in fid['/'])


    # Check that datasets can be appended correctly, with and without
    # compression
    def test_append_dataset(self):
        for dset_name, var_name in zip(self.dset_names, self.var_names):
            for comp_lvl in [None, 4, 9]:
                true_data = getattr(self, var_name)
                filepath = self.outdir + var_name + '_saved.h5'
                desc = var_name + ' description'
                with _h5py.File(filepath, 'w') as fid:
                    fid['old_data'] = 'old_data'
                if 'scalar' in dset_name:
                    _hi5.append_dataset(
                        filepath, true_data, name=dset_name, description=desc)
                else:
                    _hi5.append_dataset(
                        filepath, true_data, name=dset_name, description=desc,
                        compression_level=comp_lvl)
                self._helper_check_dataset(filepath, dset_name, true_data, desc)
                with _h5py.File(filepath, 'r') as fid:
                    self.assertTrue('old_data' in fid['/'])


    # Check that datasets can be replaced correctly, with and without
    # compression
    def test_replace_dataset(self):
        for dset_name, var_name in zip(self.dset_names, self.var_names):
            for comp_lvl in [None, 4, 9]:
                true_data = getattr(self, var_name)
                replacement_data = 2 * true_data
                filepath = self.outdir + var_name + '_saved.h5'
                desc = dset_name + ' description'
                with _h5py.File(filepath, 'w') as fid:
                    fid['old_data'] = 'old_data'
                if 'scalar' in dset_name:
                    _hi5.append_dataset(
                        filepath, true_data, name=dset_name, description=desc)
                    _hi5.replace_dataset(
                        filepath, replacement_data, name=dset_name,
                        description=desc)
                else:
                    _hi5.append_dataset(
                        filepath, true_data, name=dset_name, description=desc,
                        compression_level=comp_lvl)
                    _hi5.replace_dataset(
                        filepath, replacement_data, name=dset_name,
                        description=desc, compression_level=comp_lvl)
                self._helper_check_dataset(
                    filepath, dset_name, replacement_data, desc)
                with _h5py.File(filepath, 'r') as fid:
                    self.assertTrue('old_data' in fid['/'])


    # Check that groups and datasets can be deleted correctly
    def test_delete(self):
        for grp in self.dtype_names:
            for dset in self.array_types:
                _hi5.delete(self.filepath, '{}/{}'.format(grp, dset))
                with _h5py.File(self.filepath, 'r') as fid:
                    self.assertFalse(dset in list(fid[grp]))
            _hi5.delete(self.filepath, grp)
            with _h5py.File(self.filepath, 'r') as fid:
                self.assertFalse(grp in list(fid))


    # Check that groups and datasets can be renamed correctly
    def test_rename(self):
        for grp in self.dtype_names:
            _hi5.rename(self.filepath, grp, grp + '_mod')
            new_grp = '{}_mod'.format(grp)
            with _h5py.File(self.filepath, 'r') as fid:
                self.assertFalse(grp in list(fid))
                self.assertTrue(new_grp in list(fid))

            for dset in self.array_types:
                new_dset = '{}_mod'.format(dset)
                _hi5.rename(
                    self.filepath,
                    '{}/{}'.format(new_grp, dset),
                    '{}/{}'.format(new_grp, new_dset))
                with _h5py.File(self.filepath, 'r') as fid:
                    self.assertTrue(new_dset in list(fid[new_grp]))


    # Check that attributes can be loaded correctly
    def test_load_attributes(self):
        name = 'data'
        attributes = {'attr1': 1, 'attr2': 'two'}
        with _h5py.File(self.filepath, 'w') as fid:
            fid[name] = 'data'
            for key, val in attributes.items():
                fid[name].attrs[key] = val
        self.assertEqual(
            _hi5.load_attributes(self.filepath, name=name),
            attributes)


    # Check that attributes can be saved correctly
    def test_save_attributes(self):
        name = 'data'
        attributes = {'attr1': 1, 'attr2': 'two'}
        with _h5py.File(self.filepath, 'w') as fid:
            fid[name] = 'data'
            fid[name].attrs['old_attr'] = 'old'
        _hi5.save_attributes(self.filepath, attributes, name=name)
        with _h5py.File(self.filepath, 'r') as fid:
            self.assertTrue(dict(fid[name].attrs), attributes)
            self.assertFalse('old_attr' in fid[name].attrs)


    # Check that attributes can be appended correctly
    def test_append_attributes(self):
        name = 'data'
        attributes = {'attr1': 1, 'attr2': 'two'}
        with _h5py.File(self.filepath, 'w') as fid:
            fid[name] = 'data'
            fid[name].attrs['old_attr'] = 'old'
            _hi5.append_attributes(self.filepath, attributes, name=name)
        with _h5py.File(self.filepath, 'r') as fid:
            self.assertTrue(dict(fid[name].attrs), attributes)
            self.assertTrue('old_attr' in fid[name].attrs)


    # Check that HDF5 files can be correctly converted to NPZ files
    def test_to_npz(self):

        # Generate data
        datasets = {
            'x': _np.ones(4),
            'y': _np.arange(10),
            'z': _np.random.random((5, 6))}
        h5_path = self.outdir + 'data.h5'
        with _h5py.File(h5_path, 'w') as fid:
            for key, val in datasets.items():
                fid[key] = val
                fid['group0/{}'.format(key)] = val
                fid['group1/subgroup0/{}'.format(key)] = val
                fid['group1/subgroup1/{}'.format(key)] = val

        # Specify root level, which should save all datasets
        npz_path = self.outdir + 'data.npz'
        _hi5.to_npz(h5_path, npz_path)
        with _np.load(npz_path) as npz_data:
            for key, val in datasets.items():
                _np.testing.assert_array_equal(npz_data[key], val)
                _np.testing.assert_array_equal(
                    npz_data['group0_{}'.format(key)], val)
                _np.testing.assert_array_equal(
                    npz_data['group1_subgroup0_{}'.format(key)], val)
                _np.testing.assert_array_equal(
                    npz_data['group1_subgroup1_{}'.format(key)], val)

        # Test the specification of a group as the path, which will save only
        # the datasets in that group, and will also affect the names of the
        # arrays in the NPZ file
        npz_path = self.outdir + 'data.npz'
        _hi5.to_npz(h5_path, npz_path, name='group1')
        with _np.load(npz_path) as npz_data:
            for key, val in datasets.items():
                _np.testing.assert_array_equal(
                    npz_data['subgroup0_{}'.format(key)], val)
                self.assertEqual(
                    sorted(npz_data._files),
                    ['subgroup{:d}_{}.npy'.format(idx, key)
                     for idx in range(2)
                     for key in sorted(datasets.keys())])
        _hi5.to_npz(h5_path, npz_path, name='group1/subgroup1')
        with _np.load(npz_path) as npz_data:
            for key, val in datasets.items():
                _np.testing.assert_array_equal(npz_data[key], val)
                self.assertEqual(
                    sorted(npz_data._files),
                    ['{}.npy'.format(key) for key in sorted(datasets.keys())])

        # Test the specification of datasets as the path, which should save just
        # those datasets
        npz_path = self.outdir + 'data.npz'
        _hi5.to_npz(h5_path, npz_path, name='x')
        with _np.load(npz_path) as npz_data:
            _np.testing.assert_array_equal(npz_data['x'], datasets['x'])
            self.assertEqual(npz_data._files, ['x.npy'])
        _hi5.to_npz(h5_path, npz_path, name=['x', 'y'])
        with _np.load(npz_path) as npz_data:
            _np.testing.assert_array_equal(npz_data['x'], datasets['x'])
            _np.testing.assert_array_equal(npz_data['y'], datasets['y'])
            self.assertEqual(sorted(npz_data._files), ['x.npy', 'y.npy'])


    # Check that HDF5 files can be correctly converted from NPZ files
    def test_from_npz(self):

        # Generate data
        datasets = {
            'x': _np.ones(4),
            'y': _np.arange(10),
            'z': _np.random.random((5, 6))}
        npz_path = self.outdir + 'data.npz'
        _np.savez_compressed(npz_path, **datasets)

        # Convert data
        h5_path = self.outdir + 'data.h5'
        _hi5.from_npz(npz_path, h5_path)
        with _h5py.File(h5_path, 'r') as fid:
            for key, val in datasets.items():
                _np.testing.assert_array_equal(fid[key][()], val)


# Main routine
if __name__=='__main__':
    _unittest.main(verbosity=2)
