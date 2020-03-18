#!/usr/bin/env python

import unittest


def get_suite():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__package__)
    return suite
