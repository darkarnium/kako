''' Implements manifest driven HTTPS simulations for Kako. '''

import os
import ssl
import logging
import multiprocessing

from kako.simulation.server import tcp
from kako.simulation.server import http


class Simulation(multiprocessing.Process):
    ''' Simulation for a vulnerable HTTPS services. '''

    def __init__(self, manifest, configuration, results, *args, **kwargs):
        super(Simulation, self).__init__()

        self.log = logging.getLogger(__name__)
        self.results = results
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
            self.configuration,
            self.results
        )

        # Load the certificate relative to the simulation directory.
        certfile = os.path.join(
            os.path.realpath(self.configuration['simulations']['path']),
            self.manifest['certificate']
        )

        # Wrapper the HTTP socket with SSL.
        self.log.info("Enabling SSL with certificate from %s", certfile)
        service.socket = ssl.wrap_socket(
            service.socket,
            certfile=certfile,
            server_side=True
        )
        service.serve_forever()
