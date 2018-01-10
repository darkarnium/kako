import logging
import pprint

from kako.simulation.server import tcp
from kako.simulation.server import error
from kako.simulation.system import linux


class RequestHandler(tcp.RequestHandler):
    ''' Implements Telnet handling for client connections. '''
    port = 'UNKNOWN'
    protocol = 'tcp'
    simulation = 'UNKNOWN'
    vulnerability = 'UNKNOWN'
    simulation_version = 'UNKNOWN'

    def __init__(self, request, client_address, server):
        ''' Setup versions and system names for this service. '''
        self.prompt = '#'
        self.hostname = 'default'

        self.banner = server.manifest['server']['banner']
        self.port = server.manifest['port']
        self.version = server.manifest['version']
        self.protocol = server.manifest['protocol']
        self.simulation = server.manifest['name']
        self.simulation_version = server.manifest['version']

        self.interpreter = linux.CommandInterpreter()

        tcp.RequestHandler.__init__(self, request, client_address, server)

    def read(self, length=None):
        ''' Override base read() method with one that handles Telnet IACs. '''
        part_index = 0
        part_buffer = bytearray()
        while True:
            # Read byte-by-byte so that IACs can be handled.
            tcp.RequestHandler.read(self, 1)
            if self.buffer[0] == 255:
                tcp.RequestHandler.read(self, 1)
                # Reply to WILL with WON'T.
                if self.buffer[0] == 251:
                    tcp.RequestHandler.read(self, 1)
                    self.write(bytearray([255, 252, self.buffer[0]]))
                    continue
                # Reply to DO with DON'T.
                if self.buffer[0] == 253:
                    tcp.RequestHandler.read(self, 1)
                    self.write(bytearray([255, 254, self.buffer[0]]))
                    continue
                # If IACs sub-negotiation, process it (...by ignoring it)
                if self.buffer[0] == 250:
                    while self.buffer[0] != 240:
                        tcp.RequestHandler.read(self, 1)
                    continue

            # If it dropped through it's just data so keep it.
            part_index += 1
            part_buffer.extend(self.buffer)

            # If line-ending or the length constraint has been satisfied, bail.
            if self.buffer[0] == 10 or (length and part_index >= length):
                break

        # Fix the buffer to contain the FULL read - sans IACs.
        self.buffer = part_buffer

    def do_iacs(self):
        ''' Sends Telnet negotiation messages to the client (IAC). '''
        # Attempt at RFC854 and RFC1073 compliance.
        parameters = []
        parameters.append([255, 254, 1])   # IAC DON'T ECHO
        parameters.append([255, 254, 31])  # IAC DON'T NAWS

        # Write all negotiation messages to the client.
        for parameter in parameters:
            self.write(bytearray(parameter))

    def do_login(self):
        ''' Simulates a login prompt and captures the credentials. '''
        self.write(self.banner.encode())
        self.write(b'\r\n\r\n')
        self.write('{0} login: '.format(self.hostname).encode())
        self.read()
        self.write(b'Password: ')
        self.read()

    def do_motd(self):
        ''' Simulates an MOTD style banner (after login). '''
        self.write(b'\r\n')

    def handle(self):
        ''' Extend TCP RequestHandler to implement a fake telnet service. '''
        self.log.info(
            'Received connection from %s',
            ':'.join(str(x) for x in self.client_address)
        )

        # Negotiate with the client, and handle initial login / banner.
        try:
            self.do_iacs()
            self.do_login()
            self.do_motd()
        except error.ClientDisconnect as _:
            self.capture()
            self.log.info('Client force disconnected.')
            return

        # Kick off the REPL, and loop until do_repl returns False.
        self.log.info('Negotiation and login complete, dropping to "shell"')
        while True:
            self.write('{0} '.format(self.prompt.rstrip()).encode())
            try:
                self.read()
            except error.ClientDisconnect as _:
                self.log.info('Client force disconnected!')
                break

            # Convert read byte array into a string and process.
            cmd = ''.join(map(chr, self.buffer)).strip()
            try:
                self.write(self.interpreter.handle(cmd).encode())
            except error.ClientCommandExit as _:
                break

        # Record the interaction.
        self.capture()
