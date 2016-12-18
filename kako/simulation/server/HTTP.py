import logging
import SocketServer
import SimpleHTTPServer


class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    ''' Implements HTTP handling for client connections. '''

    def __init__(self, request, client_address, server):
        ''' Bolt on a logger to push messages back to Kako. '''
        self.log = logging.getLogger()
        self.error_message_format = ''
        SocketServer.BaseRequestHandler.__init__(
            self, request, client_address, server
        )

    def version_string(self):
        ''' Overrides built-in version headers in HTTP responses.'''
        return 'uhttpd/1.0.0'

    def capture(self, payload):
        ''' Implements 'capture' functionality for identified requests. '''
        request = []
        request.append(self.raw_requestline.rstrip())
        request.append(self.headers)
        request.append(payload)

        self.log.info('\r\n'.join(str(x) for x in request))
        return True

    def do_404(self):
        ''' Implements a generic 404 response. '''
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('No such file or directory')
        self.wfile.close()

    def do_GET(self):
        ''' Implements routing for HTTP GET requests. '''
        self.do_404()
        return True

    def do_POST(self):
        ''' Implements routing for HTTP POST requests. '''
        self.do_404()
        return True

    def do_HEAD(self):
        ''' Implements routing for HTTP HEAD requests. '''
        self.do_404()
        return True
