''' Implements manifest driven HTTPS simulations for Kako. '''

import os
import ssl
import logging

from kako.simulation.server import tcp
from kako.simulation.server import http


class Simulation(object):
    ''' Simulation for a vulnerable HTTPS services. '''

    def __init__(self, manifest, configuration):
        self.log = logging.getLogger(__name__)
        self.manifest = manifest
        self.configuration = configuration

    def run(self):
        ''' Implements the main runable for the simulation. '''
        self.log.info(
            'Setting up listener on tcp/%s', str(self.manifest['port'])
        )
        service = tcp.Server(
            ('0.0.0.0', self.manifest['port']),
            http.RequestHandler,
            self.manifest,
            self.configuration
        )

        # TODO: Allow custom SSL certificates?
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
