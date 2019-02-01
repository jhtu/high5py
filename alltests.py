import os
import sys
import unittest

from . import helper


# Discover and run tests
def run_all_tests():
    test_loader = unittest.defaultTestLoader
    test_suites = test_loader.discover(os.path.dirname(__file__))
    unittest.TextTestRunner(buffer=True).run(test_suites)


# Main routine
if __name__ == '__main__':
    helper.add_to_path('src')
    run()
