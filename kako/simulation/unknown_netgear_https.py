import os
import ssl
import logging

from kako import constant
from kako.simulation.server import TCP
from kako.simulation.server import HTTP


class RequestHandler(HTTP.RequestHandler):
    ''' Implements simulation specific logic. '''
    simulation = 'unknown_netgear_https'
    simulation_version = '0.1.0'

    def do_POST(self):
        ''' Implement known exploit routing using HTTP POST. '''
        # NetGear authentication bypass vulnerabilities.
        if self.path.split('?')[0] == '/apply_noauth.cgi':
            self.vulnerability = 'NetGear - apply_noauth authentication bypass'
            self.capture(
                self.rfile.read(
                    int(self.headers.getheader('content-length', 0))
                )
            )
            self.send_response(200, '')

        # NetGear ReadyNAS RCE.
        if self.path.split('?')[0] == '/cgi-bin/cgi_system':
            self.vulnerability = 'NetGear - cgi_system remote code execution'
            self.capture(
                self.rfile.read(
                    int(self.headers.getheader('content-length', 0))
                )
            )
            self.send_response(200, '')

    def do_GET(self):
        ''' Implement known exploit routing using HTTP GET. '''
        # Netgear authentication bypass vulnerabilities.
        if self.path.split('?')[0] == '/BRS_netgear_success.html':
            self.vulnerability = 'NetGear - BRS authentication bypass'
            self.capture('')
            self.send_response(200, '')
            return

        # For everything else, return an HTTP 401.
        self.vulnerability = 'NetGear - HTTPS access attempt'
        self.capture('')
        self.send_response(401, 'Unauthorized')
        self.send_header('WWW-Authenticate', 'Basic realm="NETGEAR R7000"')


class Simulation(object):
    ''' Simulation for a number of vulnerable HTTP services. '''

    def __init__(self, configuration):
        self.log = logging.getLogger()
        self.port = 8443
        self.configuration = configuration

    def run(self):
        ''' Implements the main runable for the simulation. '''
        self.log.info("Setting up listener on TCP/{}".format(self.port))
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
        self.log.info("Enabling SSL with certificate from {}".format(certfile))
        service.socket = ssl.wrap_socket(
            service.socket,
            certfile=certfile,
            server_side=True
        )
        service.serve_forever()
