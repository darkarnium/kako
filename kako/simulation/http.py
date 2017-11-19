''' Implements manifest driven HTTP simulations for Kako. '''

import logging

from kako.simulation.server import tcp
from kako.simulation.server import http


class Simulation(object):
    ''' Simulation for a vulnerable HTTP service. '''

    def __init__(self, manifest, configuration):
        self.log = logging.getLogger(__name__)
        self.manifest = manifest
        self.configuration = configuration

    def run(self):
        ''' Implements the main runable for the simulation. '''
        self.log.info(
            'Setting up listener on TCP/%s', str(self.manifest['port'])
        )
        service = tcp.Server(
            ('0.0.0.0', self.manifest['port']),
            http.RequestHandler,
            self.manifest,
            self.configuration
        )
        service.serve_forever()
