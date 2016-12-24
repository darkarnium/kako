import logging

from kako import constant
from kako.simulation.server import TCP
from kako.simulation.server import HTTP


class RequestHandler(HTTP.RequestHandler):
    ''' Implements simulation specific logic. '''
    simulation = 'mirai_cpeserver_soap'

    def do_POST(self):
        ''' Implement known CPEServer SOAP exploit routing. '''
        if self.path.split('?')[0] == '/UD/act':
            self.capture(
                self.rfile.read(
                    int(self.headers.getheader('content-length', 0))
                )
            )
            self.send_response(200, '')


class Simulation(object):
    ''' Simulation for a vulnerable CPEServer SOAP service. '''

    def __init__(self, configuration):
        self.log = logging.getLogger()
        self.port = 7547
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
