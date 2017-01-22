from cerberus import Validator

# Define the configuration schema (for validation).
SCHEMA = {
    'logging': {
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
    'simulation': {
        'type': 'list'
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
    v = Validator(SCHEMA)
    if not v.validate(config):
        raise AttributeError(v.errors)
