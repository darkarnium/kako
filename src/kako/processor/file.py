''' Implements a file output / results processor for Kako. '''

import os
import logging
import multiprocessing

import json


class Processor(multiprocessing.Process):
    ''' File output / results processor for Kako. '''

    def __init__(self, configuration, results, *args, **kwargs):
        super(Processor, self).__init__()

        self.log = logging.getLogger(__name__)
        self.results = results
        self.configuration = configuration
        self.output = os.path.join(
            self.configuration['results']['attributes']['path'],
            'kako.json'
        )

    def write(self, payload):
        ''' Implements a helper to write the provided payload to file. '''
        with open(self.output, 'a') as hndl:
            hndl.write(payload)
            hndl.write('\r\n')

    def run(self):
        ''' Implements the main runable for the processor. '''
        self.log.info('Setting up File results / output processor')
        while True:
            # When there is data in the queue, attempt to pull it and write to
            # the output file. If something goes awry, requeue the message
            # prior to throwing the exception.
            if self.results.qsize() > 0:
                self.log.info(
                    '%s interaction captures in the queue',
                    self.results.qsize()
                )
                interaction = self.results.get()
                self.log.debug('Attempting to write interaction to file')
                try:
                    self.write(interaction)
                except (AttributeError, IOError, PermissionError):
                    self.log.error('Requeuing interaction, as write failed...')
                    self.results.put(interaction)
                    raise
                self.log.debug('Interaction written okay')
