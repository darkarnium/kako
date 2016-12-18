import logging
import pprint
import SocketServer

from . import TCP
from . import Error


class RequestHandler(TCP.RequestHandler):
    ''' Implements Telnet handling for client connections. '''

    def __init__(self, request, client_address, server):
        ''' Setup versions and system names for this service. '''
        self.system = 'default'
        self.version = 'BusyBox v1.19.3 (2013-11-01 10:10:26 CST)'
        self.prompt = '#'

        TCP.RequestHandler.__init__(self, request, client_address, server)

    def do_cmd(self, cmd):
        ''' Perform actions based on input command. '''
        if cmd in ['busybox', '/bin/busybox', 'help']:
            self.write("{} multi-call binary.\r\n".format(self.version))
            return

        if cmd.startswith('/bin/busybox ') or cmd.startswith('busybox '):
            applet = cmd.split(' ')[1]
            self.write("{}: applet not found\r\n".format(applet))
            return

        if cmd in ['exit', 'quit', 'logout']:
            raise Error.ClientCommandExit()

        # If all else fails, raise a 'command not found'.
        raise Error.ClientCommandNotFound()

    def do_iacs(self):
        ''' Sends Telnet negotiation messages to the client (IAC). '''
        parameters = []
        parameters.append([255, 253, 31])  # IAC DO NAWS

        # Write all negotiation messages to the client.
        for parameter in parameters:
            self.write(bytes(bytearray(parameter)))

        # A response per sent IAC / parameter should be received from client.
        while True:
            self.read(3)
            if self.buffer[0] != 255:
                break

            # Sub-negotiation isn't 3-bytes, so read until EoSP (0xF0)
            if self.buffer[1] == 250:
                while self.buffer[0] != 240:
                    self.read(1)
                break

    def do_login(self):
        ''' Simulates a login prompt and captures the credentials. '''
        self.write('{} login: '.format(self.system))
        self.read(1024)
        self.write('Password: '.format(self.system))
        self.read(1024)

    def do_banner(self):
        ''' Simulates a login banner. '''
        self.write("\r\n")
        self.write('{} built-in shell (ash)\r\n'.format(self.version))
        self.write("Enter 'help' for a list of built-in commands.\r\n\r\n")

    def handle(self):
        ''' Extend TCP RequestHandler to implement a fake telnet service. '''
        self.log.info('Received connection from {}'.format(
            ':'.join(str(x) for x in self.client_address)
        ))

        # Negociate with the client, and handle initial login / banner.
        try:
            self.do_iacs()
            self.do_login()
            self.do_banner()
        except Error.ClientDisconnect as e:
            self.capture()
            self.log.info('Client force disconnected.')
            return

        # Kick off the REPL, and loop until do_repl returns False.
        self.log.info('Negotiation and login complete, dropping to "shell"')
        while True:
            self.write('{} '.format(self.prompt.rstrip()))
            try:
                self.read(1024)
            except Error.ClientDisconnect as e:
                self.log.info('Client force disconnected!')
                break

            # Read command from buffer and action accordingly.
            cmd = ''.join(map(chr, self.buffer)).strip()
            try:
                self.do_cmd(cmd)
            except Error.ClientCommandNotFound as e:
                self.write("-sh: {}: command not found\r\n".format(cmd))
            except Error.ClientCommandExit as e:
                break

        # Record the interaction.
        self.capture()
