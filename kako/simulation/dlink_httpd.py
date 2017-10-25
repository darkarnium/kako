import logging

from kako.simulation.server import TCP
from kako.simulation.server import HTTP


class RequestHandler(HTTP.RequestHandler):
    ''' Implements simulation specific logic. '''
    banner = 'httpd'
    simulation = 'dlink_httpd'
    simulation_version = '0.2.0'

    # Define the response for all invalid routes.
    route_default = {
        "code": 401,
        "text": "Unauthorized",
        "body": "",
        "headers": [
            {
                "key": "WWW-Authenticate",
                "value": "Basic realm=\"D-Link Router\""
            }
        ],
    }

    # Define all valid POST routes.
    route_post = [
        {
            "route": "/command.php",
            "response": {
                "code": 200,
                "text": "OK",
                "body": "610cker",
                "headers": None
            },
            "vulnerability": "D-Link - command.php remote code execution",
        },
        {
            "route": "/HNAP1",
            "response": {
                "code": 200,
                "text": "OK",
                "body": "",
                "headers": None,
            },
            "vulnerability": "D-Link - HNAP1 multiple vulnerabilities",
        }
    ]

    # Define all valid GET routes.
    route_get = [
        {
            "route": "/language/",
            "response": {
                "code": 200,
                "text": "OK",
                "body": "610cker",
                "headers": None
            },
            "vulnerability": "D-Link - Language remote code execution",
        },
    ]


class Simulation(object):
    ''' Simulation for a number of vulnerable HTTP services. '''

    def __init__(self, configuration):
        self.log = logging.getLogger()
        self.port = 8080
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
