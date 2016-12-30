import json
import base64


class Capture(object):
    ''' Defines a capture message for submission of results from Kako. '''

    def __init__(self, src_ip, src_port, sim_name, cap, node, sim_version):
        ''' Generates an object for this capture. '''
        self.cap = base64.b64encode('\r\n'.join(str(x) for x in cap))
        self.node = node
        self.src_ip = src_ip
        self.src_port = src_port
        self.sim_name = sim_name
        self.sim_version = sim_version

    def toJSON(self):
        ''' Provide a JSON serializer for this Object. '''
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4
        )
