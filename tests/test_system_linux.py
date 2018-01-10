''' Implements tests for the Kako Linux Command Interpreter. '''

import os
import uuid
import yaml
import unittest
import coverage

import kako


class KakoLinuxCommandInterpreterTestCase(unittest.TestCase):
    ''' Defines tests for the Linux Command Interpreter. '''

    def setUp(self):
        ''' Ensure the application is setup for testing. '''
        self.processor = kako.simulation.system.linux.CommandInterpreter()

    def tearDown(self):
        ''' Ensure everything is torn down between tests. '''
        pass

    def test_handle(self):
        ''' Ensure that the handle dispatcher works as expected. '''
        # Ensure multiple commands per line (; delimited) works.
        candidate = 'echo A; echo B; echo C; echo D'
        expected = 'A\r\nB\r\nC\r\nD\r\n'
        self.assertEqual(self.processor.handle(candidate), expected)

        # Ensure 'command not found' errors are working.
        candidate = str(uuid.uuid4())
        expected = "sh: {0}: command not found\r\n".format(candidate)
        self.assertEqual(self.processor.handle(candidate), expected)

    def test_echo(self):
        ''' Ensure that the echo 'command' works as expected. '''
        candidates = {
            # Ensure Hex encoded characters are expanded.
            'echo -e a\\x41b\\x42a\\x41b\\x42$': "aAbBaAbB$\r\n",
            # Ensure a double dash is ignored.
            'echo -- ABCDEF': "ABCDEF\r\n",
            # Ensure that echo functions as expected.
            'echo ZYXWVU': "ZYXWVU\r\n",
            # Ensure double quote stripping is working as expected.
            'echo "ZYXWVU"': "ZYXWVU\r\n",
            # Ensure double quote stripping is working as expected.
            "echo 'ZYXWVU'": "ZYXWVU\r\n",
            # TODO: This should open a multi-line string.
            'echo "ZYXWVU': "\"ZYXWVU\r\n",
            "echo 'ZYXWVU": "\'ZYXWVU\r\n"
        }

        for candidate, expected in candidates.items():
            self.assertEqual(self.processor.handle(candidate), expected)

    def test_busybox(self):
        ''' Ensure that the busybox 'command' works as expected. '''
        candidate = 'busybox MIRAI'
        expected = 'MIRAI: applet not found\r\n'
        self.assertEqual(self.processor.handle(candidate), expected)
