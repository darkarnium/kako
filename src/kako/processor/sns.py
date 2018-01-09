''' Implements an AWS SNS output / results processor for Kako. '''

import logging
import multiprocessing
import boto3

from botocore.exceptions import ClientError


class Processor(multiprocessing.Process):
    ''' AWS SNS output / results processor for Kako. '''

    def __init__(self, configuration, results, *args, **kwargs):
        super(Processor, self).__init__()

        self.log = logging.getLogger(__name__)
        self.results = results
        self.configuration = configuration

        # Bring down the logger level(s) for boto to prevent log spam during
        # AWS operations - such as pushing messages to SNS.
        logging.getLogger('boto3').setLevel(logging.WARNING)
        logging.getLogger('botocore').setLevel(logging.WARNING)

        # Setup an AWS SNS client for publishing captures.
        self.output = boto3.client(
            'sns',
            region_name=self.configuration['results']['attributes']['region']
        )

    def write(self, payload):
        ''' Implements a helper to write the provided payload to SNS. '''
        self.output.publish(
            TopicArn=self.configuration['results']['attributes']['topic'],
            Message=payload
        )

    def run(self):
        ''' Implements the main runable for the processor. '''
        self.log.info('Setting up AWS SNS results / output processor')
        while True:
            # When there is data in the queue, attempt to pull it and write to
            # the output topic. If something goes awry, requeue the message
            # prior to throwing the exception.
            if self.results.qsize() > 0:
                self.log.info(
                    '%s interaction captures in the queue',
                    self.results.qsize()
                )
                interaction = self.results.get()
                self.log.debug('Attempting to write interaction to SNS')
                try:
                    self.write(interaction)
                except (AttributeError, ClientError):
                    self.log.error('Requeuing interaction, as write failed...')
                    self.results.put(interaction)
                    raise
                self.log.debug('Interaction written okay')
