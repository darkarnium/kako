''' Implements interaction capture and serialization for Kako. '''

import json
import base64


class Capture(object):
    ''' Defines a capture message for submission of results from Kako. '''

    def __init__(self=None, destination_port=None, destination_ip=None,
                 source_ip=None, source_port=None, simulation_name=None,
                 capture=None, node=None, simulation_version=None,
                 timestamp=None, vulnerability=None):
        ''' Generates an object for this capture. '''
        self.timestamp = timestamp
        self.capture = base64.b64encode('\r\n'.join(str(x) for x in capture))
        self.vulnerability = vulnerability
        self.node = node
        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.source_ip = source_ip
        self.source_port = source_port
        self.simulation_name = simulation_name
        self.simulation_version = simulation_version

    def toJSON(self):
        ''' Provide a JSON serializer for this Object. '''
        # Convert all instance attributes to a dictionary and serialize.
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4
        )
