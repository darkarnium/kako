import time
import socket
import logging
import SocketServer
import SimpleHTTPServer
import boto3

from kako import messaging


class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    ''' Implements HTTP handling for client connections. '''
    port = 'UNKNOWN'
    protocol = 'http'
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

        self.banner = server.manifest['server']['banner']
        self.default_response = server.manifest['server']['response']

        self.routes_get = server.manifest['server']['routes']['get']
        self.routes_post = server.manifest['server']['routes']['post']
        self.routes_head = server.manifest['server']['routes']['head']
        self.routes_options = server.manifest['server']['routes']['options']

        # Suppress client errors.
        self.error_message_format = ''

        # Setup an AWS SNS client for publishing captures.
        self.sns = boto3.client(
            'sns', region_name=server.configuration['results']['region']
        )

        # Finish initialization using the parent class.
        SocketServer.BaseRequestHandler.__init__(
            self, request, client_address, server
        )

    def log_message(self, fmt, *args):
        ''' Override default STDx logger and write to Kako log handle. '''
        self.log.info(fmt % args)

    def log_error(self, fmt, *args):
        ''' Override default error logger and nerf messages. '''
        pass

    def log_request(self, code='-', size='-'):
        ''' Override default request logger and fix formatting. '''
        # Ensure both the HTTP path and command are set.
        try:
            command = self.command
        except AttributeError:
            command = 'NO_HTTP_COMMAND'
        try:
            path = self.path
        except AttributeError:
            path = 'NO_HTTP_PATH'

        # Log it.
        self.log_message(
            'Received HTTP %s for "%s" from %s. Responded with HTTP %s.',
            command,
            path,
            ':'.join(str(x) for x in self.client_address),
            str(code)
        )

    def version_string(self):
        ''' Overrides built-in version headers in HTTP responses.'''
        return self.banner

    def do_generic(self, routes):
        ''' Implements generic route handling for requests. '''
        response = None
        if self.path is not None:
            for candidate in routes:
                if self.path.split('?')[0] == candidate['route']:
                    response = candidate['response']
                    self.vulnerability = candidate['vulnerability']
                    break

        # If no match was found, use the default response.
        if response is None:
            response = self.default_response

        # Capture the request.
        self.capture(
            self.rfile.read(
                int(self.headers.getheader('content-length', 0))
            )
        )

        # Reply, bolting on any applicable headers and response body.
        self.send_response(response['code'], response['text'])
        for header in response['headers']:
            self.send_header(header['key'], header['value'])
        self.end_headers()
        self.rfile.write(response['body'])

    def do_GET(self):
        ''' Implements routing for HTTP GET requests. '''
        self.do_generic(routes=self.routes_get)

    def do_POST(self):
        ''' Implements routing for HTTP POST requests. '''
        self.do_generic(routes=self.routes_post)

    def do_HEAD(self):
        ''' Implements routing for HTTP HEAD requests. '''
        self.do_generic(routes=self.routes_head)

    def do_OPTIONS(self):
        ''' Implements routing for HTTP HEAD requests. '''
        self.do_generic(routes=self.routes_options)

    def capture(self, payload):
        ''' Implements 'capture' functionality for identified requests. '''
        request = []
        request.append(self.raw_requestline.rstrip())
        request.append(self.headers)
        request.append(payload)

        msg = messaging.capture.Capture(
            timestamp=int(time.time()),
            capture=request,
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
