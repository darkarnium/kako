''' Implements tests for the Kako Messaging Capture interface. '''

import os
import json
import unittest
import coverage

import kako


class KakoMessagingCaptureTestCase(unittest.TestCase):
    ''' Defines tests for the Kako Messaging Capture interface. '''

    def setUp(self):
        ''' Ensure the application is setup for testing. '''
        self.fixtures_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'fixtures/'
        )

    def tearDown(self):
        ''' Ensure everything is torn down between tests. '''
        pass

    def test_messaging_capture(self):
        ''' Ensure the message capture interface properly serializes JSON. '''
        capture = {
            'capture': 'CAPTURE',
            'destination_ip': '192.0.2.1',
            'destination_port': 1234,
            'node': 'NODE',
            'simulation_name': 'SIMULATION',
            'simulation_version': '0.1.0',
            'source_ip': '192.0.2.0',
            'source_port': 1234,
            'timestamp': 1515543475,
            'vulnerability': 'VULNERABILITY'
        }

        # Load the valid capture for comparison.
        with open(os.path.join(self.fixtures_path, 'valid_capture.json')) as f:
            expected = f.read()

        # Ensure that a capture object can be hydrated without error.
        candidate = kako.messaging.capture.Capture(**capture)

        # Ensure that the serialized capture is as expected.
        self.assertEqual(candidate.toJSON(), expected)
