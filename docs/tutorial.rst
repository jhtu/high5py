Tutorial
========

The following examples demonstrate how to use the ``h5io`` module to interact with HDF5 files quickly and easily.
They are also available in the source code as a Jupyter notebook.


Saving data
-----------

First, we create some test data to save to disk::

  import numpy as np
  x = np.random.random((10, 20))

We can save the data using the :meth:`h5io.h5io.save_dataset` function::

  import h5io
  h5io.save_dataset('test.h5', x)

By default, this saves the data as a dataset called *data*.
We can check this by using the :meth:`h5io.h5io.info` function::

  h5io.info('test.h5')

We see that the file ``test.h5`` contains a single dataset called *data*.
If we want to save the dataset with a custom name, we can use the ``name`` parameter::

  h5io.save_dataset('test.h5', x, name='x')
  h5io.info('test.h5')

Now the dataset is called *x*.

Note that by default, :meth:`h5io.h5io.save_dataset` overwrites files.
To add a dataset to the file, we use :meth:`h5io.h5io.append_dataset`, which is equivalent to calling :meth:`h5io.h5io.save_dataset` with ``overwrite=False``::

  y = x + 1.
  h5io.append_dataset('test.h5', y, name='y')
  h5io.info('test.h5')

Since one of the advantages of HDF5 is that it is a self-describing file format, ``h5io`` provides an easy way to add descriptions when saving datasets.
To do so, simply use the ``description`` parameter::

  h5io.save_dataset('test.h5', x, name='x', description='x data')
  h5io.append_dataset('test.h5', x, name='y', description='y data')
  h5io.info('test.h5')

We can check the value of the dataset descriptions by using the :meth:`h5io.h5io.info` function with the appropriate ``name`` value::

  h5io.info('test.h5', name='x')
  h5io.info('test.h5', name='y')

We can also save data in groups by using the ``name`` parameter::

  h5io.append_dataset('test.h5', x, name='group/x')
  h5io.append_dataset('test.h5', y, name='group/y')
  h5io.info('test.h5')

Now we see that ``test.h5`` contains two datasets (*x* and *y*) and a group (*group*) at the root level.
We can get info on the contents of the group using the :meth:``h5io.h5io.info`` function::

  h5io.info('test.h5', name='group')


Loading data
------------

Loading data is simple using :meth:`h5io.h5io.load_dataset`::

  x_load = h5io.load_dataset('test.h5', 'x')
  print(
      'Max diff b/w orig and loaded x: {:.2e}'.format(np.abs(x - x_load).max()))
  y_load = h5io.load_dataset('test.h5', 'group/y')
  print(
      'Max diff b/w orig and loaded y: {:.2e}'.format(np.abs(y - y_load).max()))


Querying files
--------------

Sometimes it is useful to query a dataset and look at its contents.
As we have seen above, we can use :meth:`h5io.h5io.info` to get info on groups and datasets.  If we set ``return_info=True``, then we can also return a dictionary of the information::

  print('FILE/ROOT INFO:')
  h5io.info('test.h5')
  print('GROUP INFO:')
  h5io.info('test.h5', name='group')
  print('DATASET INFO:')
  info = h5io.info('test.h5', name='group/x', return_info=True)
  print(info)

We can also check for the existence of a particular dataset or group using :meth:`h5io.h5io.exists`::

  print('Dataset x exists:', h5io.exists('test.h5', 'x'))
  print('Dataset z exists:', h5io.exists('test.h5', 'z'))


Saving attributes
-----------------

As alluded to above, part of what makes HDF5 a self-describing file format is that groups and datasets can have associated attributes.
We can use :meth:`h5io.h5io.save_attributes` or :meth:`h5io.h5io.append_attributes` to add attributes to a group or dataset, with the former overwriting any existing attributes and the latter simply adding to them::

  h5io.save_dataset('test.h5', 'x', name='x')
  print('DATA W/O ATTRIBUTES')
  h5io.info('test.h5', 'x')
  print('\nDATA W/ATTRIBUTES')
  h5io.save_attributes('test.h5', {'units': 'm/s', 'num_pts': x.size}, name='x')
  h5io.info('test.h5', 'x')
  print('\nDATA W/ADDED ATTRIBUTES')
  h5io.append_attributes('test.h5', {'color': 'red'}, name='x')
  h5io.info('test.h5', 'x')


Renaming objects
----------------

We can easily rename a dataset or group using :meth:`h5io.h5io.rename`::

  print('\nORIGINAL DATA')
  h5io.info('test.h5')
  h5io.info('test.h5', 'x')
  print('\nRENAMED DATA')
  h5io.rename('test.h5', 'x', 'x_new')
  h5io.info('test.h5')
  h5io.info('test.h5', 'x_new')


Working with NPZ files
----------------------

Sometimes when collaborating, it is useful to have code with as few dependencies as possible.
To help with that ``h5io`` offers methods for converting HDF5 files to and from NPZ (numpy archive) formats.
For instance, the following code saves data to HDF5, then converts the entire contents of that file to NPZ using :meth:`h5io.h5io.to_npz`::

  h5io.save_dataset('test.h5', np.random.random((2, 5)), name='group/x1')
  h5io.append_dataset('test.h5', np.random.random((2, 5)), name='group/x2')
  h5io.append_dataset('test.h5', np.random.random((3, 5)), name='y')
  h5io.append_dataset('test.h5', np.random.random((4, 5)), name='z')
  h5io.to_npz('test.h5', 'test_all.npz')

We can also save single groups/datasets, or lists of groups/datasets::

  h5io.to_npz('test.h5', 'test_z.npz', name='z')
  h5io.to_npz('test.h5', 'test_yz.npz', name=['y', 'z'])
  h5io.to_npz('test.h5', 'test_group.npz', name='group')

To load data in an NPZ file, we can use the following syntax, noting that since NPZ files don't support groups, group/dataset paths have been altered by replacing slashes with underscores::

  with np.load('test_all.npz', 'r') as data:
      print('NPZ contents:', data._files)
      x1 = data['group_x1']
      x2 = data['group_x2']
      y = data['y']
      z = data['z']
  with np.load('test_yz.npz', 'r') as data:
      print('NPZ contents:', data._files)
      y = data['y']
      z = data['z']
  with np.load('test_group.npz', 'r') as data:
      print('NPZ contents:', data._files)
      x1 = data['x1']
      x2 = data['x2']

When converting an NPZ file to HDF5, array names will be preserved::

  np.savez_compressed(
      'test.npz',
      x_npz=np.random.random((5, 2)),
      y_npz=np.random.random((6, 7)))
  h5io.from_npz('test.npz', 'test.h5')
  h5io.info('test.h5')
