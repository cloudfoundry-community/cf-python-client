#!/usr/bin/env python

import os
import sys
import unittest

def get_suite():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__package__)
    return suite
