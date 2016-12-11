import logging
import SocketServer
import SimpleHTTPServer


class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    ''' Implements HTTP handling for client connections. '''

    def __init__(self, request, client_address, server):
        ''' Bolt on a logger to push messages back to Kako. '''
        self.log = logging.getLogger()
        SocketServer.BaseRequestHandler.__init__(
            self, request, client_address, server
        )

    def capture(self):
        ''' Implements 'capture' functionality for identified requests. '''
        return True

    def do_GET(self):
        ''' Implements routing for HTTP GET requests. '''
        return True

    def do_POST(self):
        ''' Implements routing for HTTP POST requests. '''
        return True
