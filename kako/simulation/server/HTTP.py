import time
import socket
import logging
import SocketServer
import SimpleHTTPServer
import boto3

from kako import messaging


class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    ''' Implements HTTP handling for client connections. '''
    banner = 'uhttpd/1.0.0'
    simulation = 'UNKNOWN'
    vulnerability = 'UNKNOWN'
    simulation_version = 'UNKNOWN'

    # Define lists of target routes.
    route_get = []
    route_head = []
    route_post = []

    # Define a default response (404).
    default_response = {
        'code': 404,
        'text': 'Not Found',
        'body': 'No such file or directory',
        'headers': [],
    }

    def __init__(self, request, client_address, server):
        ''' Bolt on a logger to push messages back to Kako. '''
        self.log = logging.getLogger()
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
        self.log_message(
            'Received HTTP %s for "%s" from %s. Responded with HTTP %s.',
            self.command if self.command else 'NO_HTTP_COMMAND',
            self.path if self.path else 'NO_HTTP_PATH,
            ':'.join(str(x) for x in self.client_address),
            str(code)
        )

    def version_string(self):
        ''' Overrides built-in version headers in HTTP responses.'''
        return self.banner

    def do_generic(self, route_list):
        ''' Implements generic route handling for requests. '''
        response = None
        if self.path is not None:
            for candidate in route_list:
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
        self.do_generic(route_list=self.route_get)

    def do_POST(self):
        ''' Implements routing for HTTP POST requests. '''
        self.do_generic(route_list=self.route_post)

    def do_HEAD(self):
        ''' Implements routing for HTTP HEAD requests. '''
        self.do_generic(route_list=self.route_head)

    def capture(self, payload):
        ''' Implements 'capture' functionality for identified requests. '''
        request = []
        request.append(self.raw_requestline.rstrip())
        request.append(self.headers)
        request.append(payload)

        msg = messaging.capture.Capture(
            ts=int(time.time()),
            cap=request,
            vuln=self.vulnerability,
            node=socket.gethostname(),
            src_ip=self.client_address[0],
            src_port=self.client_address[1],
            sim_name=self.simulation,
            sim_version=self.simulation_version
        )

        # Publish to SNS.
        self.log.info('Publishing results from interaction to SNS.')
        self.sns.publish(
            TopicArn=self.server.configuration['results']['topic'],
            Message=msg.toJSON()
        )
