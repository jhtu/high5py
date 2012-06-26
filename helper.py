# Helper functions that are common in setting up tests.
import os
import sys
import unittest

# Add directory to sys.path for importing modules.  Directory must be a string 
# relative to the modred top level, such as "src" or "examples".  Use this
# complex function to ensure things are operating system-independent.
def add_to_path(directory):
    dir_loc = os.path.join(os.path.join(os.path.dirname(__file__), '..'),
        directory)
    if sys.path[0] != dir_loc:
        sys.path.insert(0, dir_loc)



