''' Implements tests for the Kako configuration parser. '''

import os
import yaml
import unittest
import coverage

import kako


class KakoConfigTestCase(unittest.TestCase):
    ''' Defines tests for the Kako configuration parser. '''

    def setUp(self):
        ''' Ensure the application is setup for testing. '''
        self.fixtures_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'fixtures/'
        )

    def tearDown(self):
        ''' Ensure everything is torn down between tests. '''
        pass

    def test_config_validation(self):
        ''' Ensures that configurations can be validated. '''
        # Ensure a valid config loads without error.
        valid = yaml.safe_load(
            open(os.path.join(self.fixtures_path, 'valid_config.yaml'))
        )
        self.assertIsNone(kako.config.validate(valid))

        # Ensure an invalid config throws an AttributeError
        invalid = yaml.safe_load(
            open(os.path.join(self.fixtures_path, 'invalid_config.yaml'))
        )
        self.assertRaises(AttributeError, kako.config.validate, invalid)
