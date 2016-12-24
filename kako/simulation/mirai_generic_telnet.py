import logging

from kako import constant
from kako.simulation import server


class RequestHandler(server.Telnet.RequestHandler):
    ''' Implements simulation specific logic. '''
    simulation = 'mirai_generic_telnet'

    def do_cmd(self, cmd):
        ''' Implement known Mirai telnet routing. '''
        # If all else fails, call the base implementation which handles a
        # number of generic cases (including help and 'command not found').
        server.Telnet.RequestHandler.do_cmd(self, cmd)


class Simulation(object):
    ''' Simulation for a vulnerable Telnet service. '''

    def __init__(self, configuration):
        self.log = logging.getLogger()
        self.port = 2323
        self.configuration = configuration

    def run(self):
        ''' Implements the main runable for the simulation. '''
        self.log.info("Setting up listener on TCP/{}".format(self.port))
        service = server.TCP.Server(
            ('0.0.0.0', self.port),
            RequestHandler,
            self.configuration
        )
        service.serve_forever()
