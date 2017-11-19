import logging

from kako.simulation.server import TCP
from kako.simulation.server import error
from kako.simulation.system import linux


class RequestHandler(TCP.RequestHandler):
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

        self.banner = server.manifest['banner']
        self.port = server.manifest['port']
        self.version = server.manifest['version']
        self.protocol = server.manifest['protocol']
        self.simulation = server.manifest['name']

        self.interpreter = linux.CommandInterpreter()

        TCP.RequestHandler.__init__(self, request, client_address, server)

    def do_iacs(self):
        ''' Sends Telnet negotiation messages to the client (IAC). '''
        parameters = []
        parameters.append([255, 253, 31])  # IAC DO NAWS

        # Write all negotiation messages to the client.
        for parameter in parameters:
            self.write(bytes(bytearray(parameter)))

        # A response per sent IAC / parameter should be received from client.
        while True:
            self.read(3, record=False)
            if self.buffer[0] != 255:
                break

            # Sub-negotiation isn't 3-bytes, so read until EoSP (0xF0)
            if len(self.buffer) > 2:
                if self.buffer[1] == 250:
                    while self.buffer[0] != 240:
                        self.read(1, record=False)
                    break

    def do_login(self):
        ''' Simulates a login prompt and captures the credentials. '''
        self.write('{}\r\n'.format(self.banner))
        self.write('{} login: '.format(self.hostname))
        self.read(1024)
        self.write('Password: ')
        self.read(1024)

    def do_banner(self):
        ''' Simulates an MOTD style banner (after login). '''
        self.write("\r\n")

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
            self.do_banner()
        except error.ClientDisconnect as _:
            self.capture()
            self.log.info('Client force disconnected.')
            return

        # Kick off the REPL, and loop until do_repl returns False.
        self.log.info('Negotiation and login complete, dropping to "shell"')
        while True:
            self.write('{} '.format(self.prompt.rstrip()))
            try:
                self.read(1024)
            except error.ClientDisconnect as _:
                self.log.info('Client force disconnected!')
                break

            # Convert read byte array into a string and process.
            cmd = ''.join(map(chr, self.buffer)).strip()
            try:
                self.write(self.interpreter.handle(cmd))
            except error.ClientCommandExit as _:
                break

        # Record the interaction.
        self.capture()
