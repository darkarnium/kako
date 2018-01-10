''' Implements manifest validation for Kako simulations. '''

from cerberus import Validator
from cerberus import schema_registry

# Define a generic schema for response entities.
SCHEMA_RESPONSE = {
    'code': {'type': 'integer'},
    'text': {'type': 'string'},
    'body': {'type': 'string'},
    'headers': {
        'type': 'list',
        'schema': {
            'type': 'dict',
            'schema': {
                'key': {'type': 'string'},
                'value': {'type': 'string'},
            }
        }
    }
}

# Define a generic schema for routing entities.
SCHEMA_ROUTING = {
    'type': 'dict',
    'schema': {
        'vulnerability': {'type': 'string'},
        'route': {'type': 'string'},
        'response': {
            'type': 'dict',
            'oneof_schema': [SCHEMA_RESPONSE]
        }
    }
}

# Define the configuration schema (for validation).
SCHEMA = {
    'name': {'type': 'string'},
    'port': {'type': 'integer'},
    'version': {'type': 'string'},
    'protocol': {'type': 'string'},
    'certificate': {'type': 'string'},
    'server': {
        'type': 'dict',
        'schema': {
            'banner': {'type': 'string'},
            'response': {
                'type': 'dict',
                'oneof_schema': [SCHEMA_RESPONSE]
            },
            'routes': {
                'type': 'dict',
                'schema': {
                    'patch': {
                        'type': 'list',
                        'oneof_schema': [SCHEMA_ROUTING]
                    },
                    'put': {
                        'type': 'list',
                        'oneof_schema': [SCHEMA_ROUTING]
                    },
                    'post': {
                        'type': 'list',
                        'oneof_schema': [SCHEMA_ROUTING]
                    },
                    'get': {
                        'type': 'list',
                        'oneof_schema': [SCHEMA_ROUTING]
                    },
                    'options': {
                        'type': 'list',
                        'oneof_schema': [SCHEMA_ROUTING]
                    },
                    'head': {
                        'type': 'list',
                        'oneof_schema': [SCHEMA_ROUTING]
                    },
                }
            }
        }
    }
}


def validate(config):
    ''' Test whether the provided configuration object is valid. '''
    linter = Validator(SCHEMA)
    if not linter.validate(config):
        raise AttributeError(linter.errors)
