import logging

from . import server
from kako import constant


class RequestHandler(server.TCP.RequestHandler):
    ''' Implements simulation specific logic. '''


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
