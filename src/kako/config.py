''' Implements configuration validation for Kako. '''

from cerberus import Validator

# Define a sub-schema for the result configuration for Amazon SNS.
SCHEMA_RESULTS_SNS = {
    'processor': {'type': 'string', 'allowed': ['sns']},
    'attributes': {
        'type': 'dict',
        'schema': {
            'region': {'type': 'string'},
            'topic': {'type': 'string'}
        }
    }
}

# Define a sub-schema for the result configuration for JSON.
SCHEMA_RESULTS_FILE = {
    'processor': {'type': 'string', 'allowed': ['file']},
    'attributes': {
        'type': 'dict',
        'schema': {
            'path': {'type': 'string'}
        }
    }
}

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
        'oneof_schema': [
            SCHEMA_RESULTS_SNS,
            SCHEMA_RESULTS_FILE
        ]
    }
}


def validate(config):
    ''' Test whether the provided configuration object is valid. '''
    linter = Validator(SCHEMA)
    if not linter.validate(config):
        raise AttributeError(linter.errors)
