import logging

from kako.simulation.server import TCP
from kako.simulation.server import telnet
from kako.simulation.system import linux


class CommandInterpreter(linux.CommandInterpreter):
    ''' Implements Mirai specific command interpretation. '''

    def do_wget(self, args=None):
        ''' Implement `wget` stub. '''
        if args is None:
            args = []
        return

    def do_cat(self, args=None):
        ''' Implement expected Mirai files. '''
        if args is None:
            args = []
        if len(args) < 1:
            return

        # TELNET_DETECT_ARCH - Fake ELF header.
        if args[0] == '/bin/echo':
            return ''.join([
                '\x7F\x45\x4c\x46',                  # ELF magic.
                '\x01',                              # 32-Bit.
                '\x01',                              # Little Endian.
                '\x01',                              # Version 1.
                '\x03',                              # Linux ABI.
                '\x00\x00\x00\x00\x00\x00\x00\x00',  # Unused padding.
                '\x02',                              # Executable.
                '\x08'                               # MIPS.
            ])

        # TELNET_PARSE_MOUNTS - Fake read-write mount-point(s).
        if args[0] == '/proc/mounts':
            return 'rootfs / rootfs rw 0 0'

    def do_ps(self, args=None):
        ''' Implements Mirai expected processes. '''
        if args is None:
            args = []
        process_list = []
        process_list.append("PID   Uid    VmSize    Stat    Command\r\n")
        process_list.append("  1   root      404     S      init")
        return ''.join(process_list)


class RequestHandler(telnet.RequestHandler):
    ''' Implements simulation specific logic. '''
    simulation = 'generic_telnetd'
    vulnerability = 'Generic - Telnet with default credentials'
    simulation_version = '0.3.0'

    def __init__(self, request, client_address, server):
        ''' Override the default telnet server injecting a custom interpreter. '''
        self.prompt = '#'
        self.hostname = 'default'
        self.interpreter = CommandInterpreter()
        TCP.RequestHandler.__init__(self, request, client_address, server)


class Simulation(object):
    ''' Simulation for a vulnerable Telnet service. '''

    def __init__(self, configuration):
        self.log = logging.getLogger()
        self.port = 2323
        self.configuration = configuration

    def run(self):
        ''' Implements the main runable for the simulation. '''
        self.log.info("Setting up listener on TCP/%s", str(self.port))
        service = TCP.Server(
            ('0.0.0.0', self.port),
            RequestHandler,
            self.configuration
        )
        service.serve_forever()
