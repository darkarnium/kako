''' Implements configuration validation for Kako. '''

from cerberus import Validator

# Define the configuration schema (for validation).
SCHEMA = {
    'logging': {
        'type': 'dict',
        'schema': {
            'path': {'type': 'string'}
        }
    },
    'simulations': {
        'type': 'dict',
        'schema': {
            'path': {'type': 'string'}
        }
    },
    'monitoring': {
        'type': 'dict',
        'schema': {
            'enabled': {'type': 'boolean'},
            'interval': {'type': 'integer'}
        }
    },
    'results': {
        'type': 'dict',
        'schema': {
            'region': {'type': 'string'},
            'topic': {'type': 'string'}
        }
    }
}


def validate(config):
    ''' Test whether the provided configuration object is valid. '''
    linter = Validator(SCHEMA)
    if not linter.validate(config):
        raise AttributeError(linter.errors)
