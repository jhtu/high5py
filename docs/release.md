# Release notes

## high5py 0.2

A few new features, a small bug fix, and some internal changes.

**New features and improvements**

- Added new method `load_attributes` that loads all attributes from a group/dataset and returns them as a dictionary.

**Bug fixes**

- The `start_index` and `end_index` arguments to `load_dataset` are now functional.  Previously, argument values could be passed in but would not affect the function behavior.

- Fixed a minor bug in the tutorial by updating the expected exception when trying to append a dataset whose name already exists.

**Internal changes**

- The repository files have been reorganized.

- The documentation now uses markdown syntax.

- The documentation has been modified to reduce redundant/duplicated files/text.

## high5py 0.1

First public release.
