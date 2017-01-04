import logging

from kako import constant
from kako.simulation.server import TCP
from kako.simulation.server import HTTP


class RequestHandler(HTTP.RequestHandler):
    ''' Implements simulation specific logic. '''
    simulation = 'unknown_unknown_rompager'
    simulation_version = '0.1.0'

    def version_string(self):
        ''' Implement common RomPager server version string. '''
        return 'RomPager/4.07 UPnP/1.0'

    def do_POST(self):
        ''' Implement known exploit routing using HTTP POST. '''
        # Generic RomPager vulnerabilities.
        self.vulnerability = 'Unknown - RomPager multiple vulnerabilities'
        self.capture(
            self.rfile.read(
                int(self.headers.getheader('content-length', 0))
            )
        )
        self.send_response(200, 'OK')

    def do_GET(self):
        ''' Implement known exploit routing using HTTP GET. '''
        # For everything else, return an HTTP 401.
        self.vulnerability = 'Unknown - RomPager access attempt'
        self.capture('')
        self.send_response(200, 'OK')
        self.send_header('EXT', '')


class Simulation(object):
    ''' Simulation for a number of vulnerable HTTP services. '''

    def __init__(self, configuration):
        self.log = logging.getLogger()
        self.port = 5555
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
