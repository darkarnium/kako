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
        self.node = node
        self.source_ip = source_ip
        self.timestamp = timestamp
        self.source_port = source_port
        self.vulnerability = vulnerability
        self.destination_ip = destination_ip
        self.simulation_name = simulation_name
        self.destination_port = destination_port
        self.simulation_version = simulation_version
        self.capture = base64.b64encode(''.join(capture).encode()).decode()

    def toJSON(self):
        ''' Provide a JSON serializer for this Object. '''
        return json.dumps(self.__dict__, sort_keys=True)
