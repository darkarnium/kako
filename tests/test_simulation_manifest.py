''' Implements tests for the Kako Simulation Manifest parser. '''

import os
import yaml
import unittest
import coverage

import kako


class KakoSimulationManifestTestCase(unittest.TestCase):
    ''' Defines tests for the Kako Simulation Manifest parser. '''

    def setUp(self):
        ''' Ensure the application is setup for testing. '''
        self.fixtures_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'fixtures/'
        )

    def tearDown(self):
        ''' Ensure everything is torn down between tests. '''
        pass

    def test_simulation_validation(self):
        ''' Ensure that simulation manifests can be validated. '''
        # Ensure valid manifests load without error.
        valid = yaml.safe_load(
            open(os.path.join(self.fixtures_path, 'valid_manifest.yaml'))
        )
        self.assertIsNone(kako.simulation.manifest.validate(valid))

        # Ensure invalid manifests throw an AttributeError
        invalid = yaml.safe_load(
            open(os.path.join(self.fixtures_path, 'invalid_manifest.yaml'))
        )
        self.assertRaises(
            AttributeError, kako.simulation.manifest.validate, invalid
        )
