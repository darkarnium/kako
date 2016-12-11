from cerberus import Validator

# Define the configuration schema (for validation).
SCHEMA = {
    'logging': {
        'type': 'dict',
        'schema': {
            'path': {'type': 'string'}
        }
    },
    'simulation': {
        'type': 'list'
    },
    'storage': {
        'type': 'dict',
        'schema': {
            'region': {'type': 'string'},
            'bucket': {'type': 'string'}
        }
    }
}


def validate(config):
    ''' Test whether the provided configuration object is valid. '''
    v = Validator(SCHEMA)
    if not v.validate(config):
        raise AttributeError(v.errors)
