import logging

from kako.simulation.server import TCP
from kako.simulation.server import HTTP


class RequestHandler(HTTP.RequestHandler):
    ''' Implements simulation specific logic. '''
    banner = 'RomPager/4.07 UPnP/1.0'
    simulation = 'allegro_rompager'
    simulation_version = '0.2.0'

    # Define the response for all invalid routes.
    route_default = {
        "code": 200,
        "text": "OK",
        "body": "",
        "headers": [
            {
                "key": "EXT",
                "value": ""
            }
        ],
    }


class Simulation(object):
    ''' Simulation for a number of vulnerable HTTP services. '''

    def __init__(self, configuration):
        self.log = logging.getLogger()
        self.port = 5555
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
