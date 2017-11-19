''' Implements manifest driven Telnet simulation for Kako. '''

import logging

from kako.simulation.server import tcp
from kako.simulation.server import telnet
from kako.simulation.system import linux


class CommandInterpreter(linux.CommandInterpreter):
    ''' Implements Mirai specific command interpretation. '''

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
        process_list.append('PID   Uid    VmSize    Stat    Command\r\n')
        process_list.append('  1   root      404     S      init')
        return ''.join(process_list)


class Simulation(object):
    ''' Simulation for a vulnerable Telnet service. '''

    def __init__(self, manifest, configuration):
        self.log = logging.getLogger(__name__)
        self.manifest = manifest
        self.configuration = configuration

    def run(self):
        ''' Implements the main runable for the simulation. '''
        self.log.info(
            'Setting up listener on TCP/%s', str(self.manifest['port'])
        )
        service = tcp.Server(
            ('0.0.0.0', self.manifest['port']),
            telnet.RequestHandler,
            self.manifest,
            self.configuration
        )
        service.serve_forever()
