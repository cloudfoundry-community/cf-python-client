import unittest
import logging

if __name__ == '__main__':
    from test_organizations import TestOrganizations
    from test_spaces import TestSpaces
    from test_applications import TestApplications
    logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)5s - %(name)s -  %(message)s')
    unittest.main()