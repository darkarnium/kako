''' Implements manifest validation for Kako simulations. '''

from cerberus import Validator
from cerberus import schema_registry

# TODO: Add custom objects to the Schema registry to simplify the schema
#       definition.
schema_registry.add('response', {})

# Define the configuration schema (for validation).
SCHEMA = {
    'name': {'type': 'string'},
    'port': {'type': 'integer'},
    'version': {'type': 'string'},
    'protocol': {'type': 'string'},
    'server': {
        'type': 'dict',
        'schema': {
            'banner': {'type': 'string'},
            'response': {
                'type': 'dict',
                'schema': {
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
            },
            'routes': {
                'type': 'dict',
                'schema': {
                    'post': {
                        'type': 'list',
                        'schema': {
                            'type': 'dict',
                            'schema': {
                                'vulnerability': {'type': 'string'},
                                'response': {
                                    'type': 'dict',
                                    'schema': {
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
                                },
                                'route': {'type': 'string'}
                            }
                        }
                    },
                    'get': {
                        'type': 'list',
                        'schema': {
                            'type': 'dict',
                            'schema': {
                                'vulnerability': {'type': 'string'},
                                'response': {
                                    'type': 'dict',
                                    'schema': {
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
                                },
                                'route': {'type': 'string'}
                            }
                        }
                    },
                    'options': {
                        'type': 'list',
                        'schema': {
                            'type': 'dict',
                            'schema': {
                                'vulnerability': {'type': 'string'},
                                'response': {
                                    'type': 'dict',
                                    'schema': {
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
                                },
                                'route': {'type': 'string'}
                            }
                        }
                    },
                    'head': {
                        'type': 'list',
                        'schema': {
                            'type': 'dict',
                            'schema': {
                                'vulnerability': {'type': 'string'},
                                'response': {
                                    'type': 'dict',
                                    'schema': {
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
                                },
                                'route': {'type': 'string'}
                            }
                        }
                    }
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
