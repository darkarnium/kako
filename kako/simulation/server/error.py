class ClientDisconnect(Exception):
    ''' Exception for signalling client disconnect. '''
    pass


class ClientCommandExit(Exception):
    ''' Exception for signalling client requested 'exit'. '''
    pass


class ClientCommandNotFound(Exception):
    ''' Exception for signalling command not found. '''
    pass
