import unittest
import os
import shutil

import numpy as np
import h5py
import h5io


class TestH5IO(unittest.TestCase):
    def setUp(self):
        self.outdir = os.path.join(os.path.dirname(__file__), 'tmp/')
        self.file_path = self.outdir + 'test_file.py'
        if not os.path.isdir(self.outdir):
            os.mkdir(self.outdir)
        self.generate_data()


    def tearDown(self):
        shutil.rmtree(self.outdir, ignore_errors=True)


    def generate_data(self):
        # Types of data to create
        self.dtype_names = ['int', 'float', 'complex']
        self.array_types = ['scalar', 'vector', 'array']
        self.dset_names = ['%s_%s' % (d_type, a_type)
            for d_type in self.dtype_names for a_type in self.array_types]
        self.num_rows = np.random.randint(2, 10)
        self.num_cols = np.random.randint(2, 10)

        # Make some scalar data (create an array first, so that the type is
        # np.int32, not int, for later comparisons)
        self.int_scalar = np.array(np.random.randint(-10, 10))[()]
        self.float_scalar = np.array(np.random.rand())[()]
        self.complex_scalar = np.array(
            np.random.rand() + 1j * np.random.rand())[()]

        # Make some vector data
        self.int_vector = np.random.randint(-10, 10, size=self.num_rows)
        self.float_vector = np.random.rand(self.num_rows)
        self.complex_vector = (
            np.random.rand(self.num_rows) + 1j * np.random.rand(self.num_rows))

        # Make some array data
        self.int_array = np.random.randint(
            -10, 10, size=(self.num_rows, self.num_cols))
        self.float_array = np.random.rand(self.num_rows, self.num_cols)
        self.complex_array = (
            np.random.rand(self.num_rows, self.num_cols) +
            1j * np.random.rand(self.num_rows, self.num_cols))

        # Save to HDF5 file
        with h5py.File(self.file_path, 'w') as fid:
            for dset_name in self.dset_names:
                fid[dset_name] = getattr(self, dset_name)


    # Check equality for both arrays and scalars
    def _helper_assert_equal(self, test_data, true_data):
        self.assertEqual(type(test_data), type(true_data))
        if isinstance(true_data, np.ndarray):
            np.testing.assert_array_equal(test_data, true_data)
        else:
            self.assertEqual(test_data, true_data)


    # Check that a dataset inside an HDF5 file is correct
    def _helper_check_dataset(
        self, file_path, dset_name, true_data, desc):

        # Open file
        with h5py.File(file_path, 'r') as fid:

            # Check that dataset exists
            self.assertTrue(dset_name in list(fid))

            # Check description of dataset
            self.assertEqual(fid[dset_name].attrs['Description'], desc)

            # Check values
            saved_data = fid[dset_name][()]
            self._helper_assert_equal(saved_data, true_data)


    # Check that existence of groups/datasets can be queried correctly
    def test_exists(self):
        with h5py.File(self.file_path, 'w') as fid:
            fid['existing/dataset'] = 'data_string'
        self.assertTrue(h5io.exists(self.file_path, 'existing'))
        self.assertTrue(h5io.exists(self.file_path, 'existing/dataset'))
        self.assertFalse(h5io.exists(self.file_path, 'existing/other'))
        self.assertFalse(h5io.exists(self.file_path, 'nonexistent/dataset'))


    # Check that datasets can be loaded correctly
    def test_load_dataset(self):
        for dset_name in self.dset_names:
            loaded_data = h5io.load_dataset(self.file_path, dset_name)
            true_data = getattr(self, dset_name)
            self._helper_assert_equal(loaded_data, true_data)


    # Check that datasets can be saved correctly
    def test_save_dataset(self):
        for dset_name in self.dset_names:
            true_data = getattr(self, dset_name)
            file_path = self.outdir + dset_name + '_saved.h5'
            desc = dset_name + ' description'
            h5io.save_dataset(
                file_path, true_data, dataset_path=dset_name, description=desc)
            self._helper_check_dataset(file_path, dset_name, true_data, desc)


    # Check that datasets can be renamed correctly
    def test_rename_dataset(self):
        for dset_name in self.dset_names:
            h5io.rename_dataset(
                self.file_path, dset_name, dset_name + '_mod')
            with h5py.File(self.file_path, 'r') as fid:
                self.assertFalse(dset_name in list(fid))
                self.assertTrue(dset_name + '_mod' in list(fid))


    # Check that HDF5 files can be correctly converted to NPZ files
    def test_to_npz(self):

        # Generate data
        datasets = {
            'x': np.ones(4), 'y': np.arange(10), 'z': np.random.random((5, 6))}
        h5_path = self.outdir + 'data.h5'
        with h5py.File(h5_path, 'w') as fid:
            for key, val in datasets.items():
                fid[key] = val
                fid['group0/{}'.format(key)] = val
                fid['group1/subgroup0/{}'.format(key)] = val
                fid['group1/subgroup1/{}'.format(key)] = val

        # Specify root level, which should save all datasets
        npz_path = self.outdir + 'data.npz'
        h5io.to_npz(h5_path, npz_path)
        with np.load(npz_path) as npz_data:
            for key, val in datasets.items():
                np.testing.assert_array_equal(npz_data[key], val)
                np.testing.assert_array_equal(
                    npz_data['group0_{}'.format(key)], val)
                np.testing.assert_array_equal(
                    npz_data['group1_subgroup0_{}'.format(key)], val)
                np.testing.assert_array_equal(
                    npz_data['group1_subgroup1_{}'.format(key)], val)

        # Test the specification of a group as the path, which will save only
        # the datasets in that group, and will also affect the names of the
        # arrays in the NPZ file
        npz_path = self.outdir + 'data.npz'
        h5io.to_npz(h5_path, npz_path, path='group1')
        with np.load(npz_path) as npz_data:
            for key, val in datasets.items():
                np.testing.assert_array_equal(
                    npz_data['subgroup0_{}'.format(key)], val)
                self.assertEqual(
                    sorted(npz_data._files),
                    ['subgroup{:d}_{}.npy'.format(idx, key)
                     for idx in range(2)
                     for key in sorted(datasets.keys())])
        h5io.to_npz(h5_path, npz_path, path='group1/subgroup1')
        with np.load(npz_path) as npz_data:
            for key, val in datasets.items():
                np.testing.assert_array_equal(npz_data[key], val)
                self.assertEqual(
                    sorted(npz_data._files),
                    ['{}.npy'.format(key) for key in sorted(datasets.keys())])

        # Test the specification of datasets as the path, which should save just
        # those datasets
        npz_path = self.outdir + 'data.npz'
        h5io.to_npz(h5_path, npz_path, path='x')
        with np.load(npz_path) as npz_data:
            np.testing.assert_array_equal(npz_data['x'], datasets['x'])
            self.assertEqual(npz_data._files, ['x.npy'])
        h5io.to_npz(h5_path, npz_path, path=['x', 'y'])
        with np.load(npz_path) as npz_data:
            np.testing.assert_array_equal(npz_data['x'], datasets['x'])
            np.testing.assert_array_equal(npz_data['y'], datasets['y'])
            self.assertEqual(sorted(npz_data._files), ['x.npy', 'y.npy'])


    # Check that HDF5 files can be correctly converted from NPZ files
    def test_from_npz(self):

        # Generate data
        datasets = {
            'x': np.ones(4), 'y': np.arange(10), 'z': np.random.random((5, 6))}
        npz_path = self.outdir + 'data.npz'
        np.savez_compressed(npz_path, **datasets)

        # Convert data
        h5_path = self.outdir + 'data.h5'
        h5io.from_npz(npz_path, h5_path)
        with h5py.File(h5_path, 'r') as fid:
            for key, val in datasets.items():
                np.testing.assert_array_equal(fid[key][()], val)


# Main routine
if __name__=='__main__':
    unittest.main(verbosity=2)
