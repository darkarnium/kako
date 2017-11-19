import time
import logging
import socket
import SocketServer
import boto3

from kako import messaging
from kako.simulation.server import error


class RequestHandler(SocketServer.BaseRequestHandler):
    ''' Implements TCP handling for client connections. '''
    port = 'UNKNOWN'
    protocol = 'tcp'
    simulation = 'UNKNOWN'
    vulnerability = 'UNKNOWN'
    simulation_version = 'UNKNOWN'

    def __init__(self, request, client_address, server):
        ''' Extends parent with additional SNS channel and logger. '''
        self.log = logging.getLogger(__name__)
        self.port = server.manifest['port']
        self.version = server.manifest['version']
        self.protocol = server.manifest['protocol']
        self.simulation = server.manifest['name']
        self.simulation_version = server.manifest['version']

        # Results tracking.
        self.buffer = []
        self.record = []

        # Setup an AWS SNS client for publishing captures.
        self.sns = boto3.client(
            'sns', region_name=server.configuration['results']['region']
        )

        # Finish initialization using the parent class.
        SocketServer.BaseRequestHandler.__init__(
            self, request, client_address, server
        )

    def write(self, message):
        ''' Writes to the socket. '''
        self.request.sendall(message)

    def read(self, length, record=True):
        ''' Reads from the socket into the record and build a byte-array. '''
        raw = self.request.recv(length)
        if raw == '':
            raise error.ClientDisconnect()

        # If requested, save the read data into the record buffer, and stuff
        # it into the read buffer eitherway.
        if record:
            self.record.append(raw.strip())
        self.buffer = map(ord, list(raw))

    def capture(self):
        ''' Implements 'capture' functionality for identified requests. '''
        msg = messaging.capture.Capture(
            timestamp=int(time.time()),
            capture=self.record,
            vulnerability=self.vulnerability,
            node=socket.gethostname(),
            destination_ip='TODO',
            destination_port=self.port,
            source_ip=self.client_address[0],
            source_port=self.client_address[1],
            simulation_name=self.simulation,
            simulation_version=self.simulation_version
        )

        # Publish to SNS.
        self.log.info('Publishing results from interaction to SNS.')
        self.sns.publish(
            TopicArn=self.server.configuration['results']['topic'],
            Message=msg.toJSON()
        )


class Server(SocketServer.ThreadingTCPServer):
    ''' Extends SocketServer ThreadingTCPServer to provide configurability. '''

    def __init__(self, server_address, RequestHandlerClass, manifest, configuration):
        SocketServer.ThreadingTCPServer.__init__(
            self, server_address, RequestHandlerClass
        )
        self.configuration = configuration
        self.manifest = manifest
