import logging

from kako import constant
from kako.simulation.server import TCP
from kako.simulation.server import HTTP


class RequestHandler(HTTP.RequestHandler):
    ''' Implements simulation specific logic. '''
    simulation = 'unknown_dlink_http'
    simulation_version = '0.1.0'

    def version_string(self):
        ''' Implement common D-Link server version string. '''
        return 'httpd'

    def do_POST(self):
        ''' Implement known exploit routing using HTTP POST. '''
        # Generic D-Link command injection ('610ocker').
        if self.path.split('?')[0] == '/command.php':
            self.vulnerability = 'D-Link - command.php remote code execution'
            self.capture(
                self.rfile.read(
                    int(self.headers.getheader('content-length', 0))
                )
            )
            self.send_response(200, 'OK')
            self.end_headers()
            self.wfile.write('610cker')

        # Generic D-Link (et al.) HNAP1 vulnerabilities.
        if self.path.split('?')[0] == '/HNAP1':
            self.vulnerability = 'D-Link - HNAP1 multiple vulnerabilities'
            self.capture(
                self.rfile.read(
                    int(self.headers.getheader('content-length', 0))
                )
            )
            self.send_response(200, 'OK')

    def do_GET(self):
        ''' Implement known exploit routing using HTTP GET. '''
        if self.path.split('?')[0].startswith('/language/'):
            self.vulnerability = 'D-Link - Language remote code execution'
            self.capture(
                self.rfile.read(
                    int(self.headers.getheader('content-length', 0))
                )
            )
            self.send_response(200, 'OK')
            self.end_headers()
            self.wfile.write('610cker')
            return

        # For everything else, return an HTTP 401.
        self.vulnerability = 'D-Link - HTTP access attempt'
        self.capture('')
        self.send_response(401, 'Unauthorized')
        self.send_header('WWW-Authenticate', 'Basic realm="D-Link Router"')


class Simulation(object):
    ''' Simulation for a number of vulnerable HTTP services. '''

    def __init__(self, configuration):
        self.log = logging.getLogger()
        self.port = 8080
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
