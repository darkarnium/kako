import time
import logging
import socket
import socketserver

from kako import messaging

from kako.simulation.server import error


class RequestHandler(socketserver.BaseRequestHandler):
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
        self.buffer = bytearray()
        self.record = bytearray()

        # Finish initialization using the parent class.
        socketserver.BaseRequestHandler.__init__(
            self, request, client_address, server
        )

    def write(self, message):
        ''' Writes to the socket. '''
        self.request.sendall(message)

    def read(self, length):
        ''' Reads from the socket into the record and build a byte-array. '''
        self.buffer = bytearray(self.request.recv(length))
        if not self.buffer:
            raise error.ClientDisconnect()

        # Save the read data into the record buffer.
        self.record.extend(self.buffer)

    def capture(self):
        ''' Implements 'capture' functionality for identified requests. '''
        msg = messaging.capture.Capture(
            timestamp=int(time.time()),
            capture=self.record.decode(errors='backslashreplace'),
            vulnerability=self.vulnerability,
            node=socket.gethostname(),
            destination_ip='TODO',
            destination_port=self.port,
            source_ip=self.client_address[0],
            source_port=self.client_address[1],
            simulation_name=self.simulation,
            simulation_version=self.simulation_version
        )

        # Publish to results queue.
        self.log.info('Publishing results from interaction to queue')
        self.server.results.put(msg.toJSON())


class Server(socketserver.ThreadingTCPServer):
    ''' Extends SocketServer ThreadingTCPServer to provide configurability. '''

    def __init__(self, server_address, RequestHandlerClass, manifest,
                 configuration, results):
        socketserver.ThreadingTCPServer.__init__(
            self, server_address, RequestHandlerClass
        )
        self.configuration = configuration
        self.manifest = manifest
        self.results = results
