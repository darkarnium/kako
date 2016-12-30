import boto3
import socket
import logging
import SocketServer
import SimpleHTTPServer

from kako import messaging


class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    ''' Implements HTTP handling for client connections. '''
    simulation = 'UNKNOWN'

    def __init__(self, request, client_address, server):
        ''' Bolt on a logger to push messages back to Kako. '''
        self.log = logging.getLogger()
        self.error_message_format = ''

        # Setup an AWS SNS client for publishing captures.
        self.sns = boto3.client(
            'sns', region_name=self.server.configuration['results']['region']
        )

        # Finish initialization using the parent class.
        SocketServer.BaseRequestHandler.__init__(
            self, request, client_address, server
        )

    def log_message(self, format, *args):
        ''' Override default STDx logger and write to Kako log handle. '''
        self.log.info(format % args)

    def log_error(self, format, *args):
        ''' Override default error logger and nerf messages. '''
        pass

    def log_request(self, code='-', size='-'):
        ''' Override default request logger and fix formatting. '''
        self.log_message(
            'Received HTTP %s for "%s" from %s. Responded with HTTP %s.',
            self.command,
            self.path,
            ':'.join(str(x) for x in self.client_address),
            str(code)
        )

    def version_string(self):
        ''' Overrides built-in version headers in HTTP responses.'''
        return 'uhttpd/1.0.0'

    def do_GET(self):
        ''' Implements routing for HTTP GET requests. '''
        self.send_response(404, 'No such file or directory')

    def do_POST(self):
        ''' Implements routing for HTTP POST requests. '''
        self.send_response(404, 'No such file or directory')

    def do_HEAD(self):
        ''' Implements routing for HTTP HEAD requests. '''
        self.send_response(404, 'No such file or directory')

    def capture(self, payload):
        ''' Implements 'capture' functionality for identified requests. '''
        request = []
        request.append(self.raw_requestline.rstrip())
        request.append(self.headers)
        request.append(payload)

        msg = messaging.capture.Capture(
            node=socket.gethostname(),
            capture=request,
            source_ip=self.client_address[0],
            source_port=self.client_address[1],
            simulation=self.simulation
        )

        # Publish to SNS.
        self.log.info('Publishing results from interaction to SNS.')
        self.sns.publish(
            TopicArn=self.server.configuration['results']['topic'],
            Message=msg.toJSON()
        )
