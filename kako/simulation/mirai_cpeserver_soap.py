import logging

from . import server
from kako import constant


class RequestHandler(server.HTTP.RequestHandler):
    ''' Implements simulation specific logic. '''

    def do_POST(self):
        ''' Implements HTTP POST request routing. '''
        if self.path.split('?')[0] == '/UD/act':
            self.capture()


class Simulation(object):
    ''' Simulation for a vulnerable CPEServer SOAP service. '''

    def __init__(self, configuration):
        self.log = logging.getLogger()
        self.port = 7547
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
