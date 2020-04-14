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
        shutil.rmtree(self.outdir)


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


    # Check that a dataset inside an HDF5 file is correct.  The data for
    # comparison are passed in as an argument, but the descriptions are
    # hard-coded into this function.
        # Check that dataset exists, check description of dataset
        fid = h5py.File(file_path, 'r')
        self.assertTrue(dset_name in list(fid))
        self.assertEqual(fid[dset_name].attrs['Description'], desc)
    def _helper_check_dataset(
        self, file_path, dset_name, true_data, desc):

        # Check values
        saved_data = fid[dset_name][...]
        self._helper_assert_equal(saved_data, true_data)
        fid.close()


    # Check that an HDF5 can correctly be queried for the existence of a group/
    # dataset
    def test_exists(self):
        fid = h5py.File(self.file_path, 'w')
        fid['existing_dataset'] = 'data_string'
        fid.close()
        self.assertTrue(h5io.exists(self.file_path, 'existing_dataset'))
        self.assertFalse(h5io.exists(self.file_path, 'nonexistent_dataset'))


    # Check that the data that was generated and saved by generate_data() is
    # loaded correctly
    def test_load_dataset(self):
        for dset_name in self.dset_names:
            loaded_data = h5io.load_dataset(self.file_path, dset_name)
            true_data = getattr(self, dset_name)
            self._helper_assert_equal(loaded_data, true_data)


    def test_save_array(self):
    # Save generated data to HDF5 file and check that contents are correct
        for dset_name in self.dset_names:
            true_data = getattr(self, dset_name)
            file_path = self.outdir + dset_name + '_saved.h5'
            desc = dset_name + ' description'
            h5io.save_array(file_path, true_data, dset_name, desc)
            self._helper_check_dataset(file_path, dset_name, true_data, desc)


# Main routine
if __name__=='__main__':
    unittest.main(verbosity=2)
