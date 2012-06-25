import unittest
import os
import subprocess as sp

import numpy as np
import h5py 
import h5io 


class TestH5IO(unittest.TestCase):
    def setUp(self):
        self.outdir = os.path.join(os.path.dirname(__file__), 'tmp/')
        self.file_path = self.outdir + 'test_file.py'
        if not os.path.isdir(self.outdir):        
            sp.call(['mkdir', self.outdir])
        self.generate_data()


    def tearDown(self):
        sp.call(['rm -rf ' + self.outdir], shell=True)


    def generate_data(self):
        # Types of data to create
        self.data_types = ['int', 'float', 'complex']
        self.array_types = ['scalar', 'vector', 'array']
        self.dset_names = ['%s_%s' % (d_type, a_type) 
            for d_type in self.data_types for a_type in self.array_types]
        self.rows = np.random.randint(2, 10)
        self.cols = np.random.randint(2, 10)

        # Make some scalar data
        self.int_scalar = np.random.randint(-10, 10)
        self.float_scalar = np.random.rand()
        self.complex_scalar = np.random.rand() + 1j* np.random.rand()
        
        # Make some vector data
        self.int_vector = np.random.randint(-10, 10, size=self.rows) 
        self.float_vector = np.random.rand(self.rows) 
        self.complex_vector = np.random.rand(self.rows) +\
            1j * np.random.rand(self.rows) 

        # Make some array data
        self.int_array = np.random.randint(-10, 10, 
            size=(self.rows, self.cols))
        self.float_array = np.random.rand(self.rows, self.cols) 
        self.complex_array = np.random.rand(self.rows, self.cols) +\
            1j * np.random.rand(self.rows, self.cols) 
        
        # Save to hdf5 file
        fid = h5py.File(self.file_path, 'w')
        for dset_name in self.dset_names:
            fid[dset_name] = getattr(self, dset_name)
        fid.close()


    # Check equality for both arrays or scalars
    def _helper_assert_equal(self, test_data, true_data):
        if isinstance(true_data, np.ndarray):
            np.testing.assert_array_equal(test_data, true_data)
        else:
            self.assertEqual(test_data, true_data)


    # Check that a dataset inside an hdf5 file is correct.  The data for
    # comparison are passed in as an argument, but the descriptions are
    # hard-coded into this function.
    def _helper_check_dataset(self, file_path, dset_name, true_data, 
        description):
        # Check that dataset exists, check description of dataset
        fid = h5py.File(file_path, 'r')
        self.assertTrue(dset_name in list(fid))
        self.assertEqual(fid[dset_name].attrs['Description'], description)

        # If data is complex, check that real, imag parts are defined, and check
        # their descriptions
        if np.iscomplexobj(true_data):
            for part, part_desc in zip(['real', 'imag'], ['Real', 'Imaginary']):
                self.assertTrue(part in list(fid[dset_name]))
                dset_name_part = '%s/%s' % (dset_name, part)
                self.assertEqual(fid[dset_name_part].attrs['Description'], 
                    part_desc + ' part')
                saved_data = fid[dset_name_part][...]
                self._helper_assert_equal(saved_data, getattr(true_data, part))
        # If data is real, check value
        else:
            saved_data = fid[dset_name][...]
            self._helper_assert_equal(saved_data, true_data)
        fid.close()


    # Check that the data that was generated and saved by generate_data() is 
    # loaded correctly.
    def test_load_dataset(self):
        for dset_name in self.dset_names:
            loaded_data = h5io.load_dataset(self.file_path, dset_name) 
            true_data = getattr(self, dset_name)
            self._helper_assert_equal(loaded_data, true_data)


    # Take generated data and save to file.  Then check that contents of hdf5 
    # file are correct
    def test_save_array(self):
        for dset_name in self.dset_names:
            true_data = getattr(self, dset_name)
            file_path = self.outdir + dset_name + '_saved.h5'
            description = dset_name + ' description'
            h5io.save_array(file_path, true_data, dset_name, description)
            self._helper_check_dataset(file_path, dset_name, true_data, 
                description)


    # Check that a single scalar can be appended to a file correctly.  Check
    # this separately from the case where many scalars are appended to ensure
    # that the case of a float argument (as opposed to a list) is correctly
    # handled.
    def test_append_single_scalars(self):
        file_path = self.outdir + 'append_single_test.h5'
        fid = h5py.File(file_path, 'w')
        fid.close()
       
        for d_type in self.data_types:
            dset_name = '%s_scalar' % d_type
            true_data = getattr(self, dset_name)
            name = dset_name
            description = dset_name + ' description'
            h5io.append_scalars(file_path, true_data, name, description)
            self._helper_check_dataset(file_path, dset_name, true_data, 
                description)
    
    
    # Check that multiple scalars can be appended to a file correctly.
    def test_append_multiple_scalars(self):
        file_path = self.outdir + 'append_multi_test.h5'
        fid = h5py.File(file_path, 'w')
        fid.close()

        dset_name_list = ['%s_scalar' % d_type for d_type in self.data_types]
        true_data_list = [getattr(self, dset_name) for dset_name in 
            dset_name_list]
        description_list = [dset_name + ' description' for dset_name in 
            dset_name_list]
        h5io.append_scalars(file_path, true_data_list, dset_name_list, 
            description_list)
        for name, data, desc in zip(dset_name_list, true_data_list, 
            description_list):
            self._helper_check_dataset(file_path, name, data, desc)
        

# Main routine
if __name__=='__main__':
    unittest.main(verbosity=2)


