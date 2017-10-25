import logging

from kako.simulation.server import TCP
from kako.simulation.server import HTTP


class RequestHandler(HTTP.RequestHandler):
    ''' Implements simulation specific logic. '''
    banner = 'gSOAP/2.7'
    simulation = 'cpeserver_soap'
    simulation_version = '0.3.0'

    routes_post = [
        {
            "route": "/UD/act",
            "response": "",
            "vulnerability": "Generic - TR-069 SOAP remote code execution",
        }
    ]


class Simulation(object):
    ''' Simulation for a vulnerable CPEServer SOAP service. '''

    def __init__(self, configuration):
        self.log = logging.getLogger()
        self.port = 7547
        self.configuration = configuration

    def run(self):
        ''' Implements the main runable for the simulation. '''
        self.log.info("Setting up listener on TCP/%s", str(self.port))
        service = TCP.Server(
            ('0.0.0.0', self.port),
            RequestHandler,
            self.configuration
        )
        service.serve_forever()
