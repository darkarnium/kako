import logging
import SocketServer


class RequestHandler(SocketServer.BaseRequestHandler):
    ''' Implements TCP handling for client connections. '''

    def __init__(self, request, client_address, server):
        ''' Bolt on a logger to push messages back to Kako. '''
        self.log = logging.getLogger()
        SocketServer.BaseRequestHandler.__init__(
            self, request, client_address, server
        )

    def capture(self):
        ''' Implements 'capture' functionality for identified requests. '''
        return True


class Server(SocketServer.ThreadingTCPServer):
    ''' Extends SocketServer ThreadingTCPServer to provide configuration. '''

    def __init__(self, server_address, RequestHandlerClass, configuration):
        SocketServer.ThreadingTCPServer.__init__(
            self, server_address, RequestHandlerClass
        )
        self.configuration = configuration
