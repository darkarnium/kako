import logging

from kako import constant
from kako.simulation.server import TCP
from kako.simulation.server import telnet
from kako.simulation.system import linux


class CommandInterpreter(linux.CommandInterpreter):
    ''' Implements simulation specific command interpretation. '''

    def do_derp(self, args=[]):
        ''' Returns `derp` command output. '''
        return 'Derp.'


class RequestHandler(telnet.RequestHandler):
    ''' Implements simulation specific logic. '''
    simulation = 'mirai_generic_telnet'

    def __init__(self, request, client_address, server):
        ''' Override the default telnet server injecting a custom interpreter. '''
        self.prompt = '#'
        self.hostname = 'default'
        self.interpreter = CommandInterpreter()
        TCP.RequestHandler.__init__(self, request, client_address, server)


class Simulation(object):
    ''' Simulation for a vulnerable Telnet service. '''

    def __init__(self, configuration):
        self.log = logging.getLogger()
        self.port = 2323
        self.configuration = configuration

    def run(self):
        ''' Implements the main runable for the simulation. '''
        self.log.info("Setting up listener on TCP/{}".format(self.port))
        service = TCP.Server(
            ('0.0.0.0', self.port),
            RequestHandler,
            self.configuration
        )
        service.serve_forever()
