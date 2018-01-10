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
        expected = 'A\nB\nC\nD\n'
        self.assertEqual(self.processor.handle(candidate), expected)

        # Ensure 'command not found' errors are working.
        candidate = str(uuid.uuid4())
        expected = "sh: {0}: command not found\n".format(candidate)
        self.assertEqual(self.processor.handle(candidate), expected)

    def test_echo(self):
        ''' Ensure that the echo 'command' works as expected. '''
        # Ensure Hex encoded characters are expanded.
        candidate = 'echo -e a\\x41b\\x42a\\x41b\\x42$'
        expected = 'aAbBaAbB$\n'
        self.assertEqual(self.processor.handle(candidate), expected)

        # Ensure a double dash is ignored.
        candidate = 'echo -- ABCDEF'
        expected = 'ABCDEF\n'
        self.assertEqual(self.processor.handle(candidate), expected)

        # Ensure that echo functions as expected.
        candidate = 'echo ZYXWVU'
        expected = 'ZYXWVU\n'
        self.assertEqual(self.processor.handle(candidate), expected)

    def test_busybox(self):
        ''' Ensure that the busybox 'command' works as expected. '''
        candidate = 'busybox MIRAI'
        expected = 'MIRAI: applet not found\n'
        self.assertEqual(self.processor.handle(candidate), expected)
