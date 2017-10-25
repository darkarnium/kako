import os
import ssl
import logging

from kako.simulation.server import TCP
from kako.simulation.server import HTTP


class RequestHandler(HTTP.RequestHandler):
    ''' Implements simulation specific logic. '''
    banner = None
    simulation = 'netgear_https'
    simulation_version = '0.2.0'

    # Define the response for all invalid routes.
    route_default = {
        "code": 401,
        "text": "Unauthorized",
        "body": "",
        "headers": [
            {
                "key": "WWW-Authenticate",
                "value": "Basic realm=\"NETGEAR R7000\""
            }
        ],
    }

    # Define all valid POST routes.
    route_post = [
        {
            "route": "/apply_noauth.cgi",
            "response": {
                "code": 200,
                "text": "OK",
                "body": "",
                "headers": None
            },
            "vulnerability": "NetGear - apply_noauth authentication bypass",
        },
        {
            "route": "/cgi-bin/cgi_system",
            "response": {
                "code": 200,
                "text": "OK",
                "body": "",
                "headers": None,
            },
            "vulnerability": "NetGear - cgi_system remote code execution",
        }
    ]

    # Define all valid GET routes.
    route_get = [
        {
            "route": "/BRS_netgear_success.html",
            "response": {
                "code": 200,
                "text": "OK",
                "body": "",
                "headers": None
            },
            "vulnerability": "NetGear - BRS authentication bypass",
        },
    ]


class Simulation(object):
    ''' Simulation for a number of vulnerable HTTP services. '''

    def __init__(self, configuration):
        self.log = logging.getLogger()
        self.port = 8443
        self.configuration = configuration

    def run(self):
        ''' Implements the main runable for the simulation. '''
        self.log.info("Setting up listener on TCP/%s", str(self.port))
        service = TCP.Server(
            ('0.0.0.0', self.port),
            RequestHandler,
            self.configuration
        )

        # TODO: Put this in configuration.
        certfile = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '../../',
            'conf/routerlogin.pem'
        )

        # Wrapper the HTTP socket with SSL.
        self.log.info("Enabling SSL with certificate from %s", certfile)
        service.socket = ssl.wrap_socket(
            service.socket,
            certfile=certfile,
            server_side=True
        )
        service.serve_forever()
