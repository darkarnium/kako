''' Implements Linux command-line (Busybox) emulation for Kako. '''

import re

from kako.simulation.server import error


class CommandInterpreter(object):
    ''' Implements commands for an embedded BusyBox system (Linux). '''
    version = 'BusyBox v1.19.3 (2013-11-01 10:10:26 CST)'

    def do_busybox(self, args=None):
        ''' Wrapper the handle() method to handle BusyBox applets. '''
        if args:
            result = self.handle(' '.join(args))
            if re.match(r'^sh:\s', result):
                return '{}: applet not found'.format(args[0])
            else:
                return result
        else:
            return self.version

    def do_echo(self, args=None):
        ''' Returns the input as provided - sans 'arguments' '''
        if args is None:
            args = []

        # Remove any 'arguments' from echo only if contiguous and before any
        # other data.
        for idx, arg in enumerate(args):
            if arg.startswith('-'):
                del args[idx]
            else:
                break

        return ' '.join(args).strip()

    def do_id(self, args=None):
        ''' Returns `id` command output. '''
        if args is None:
            args = []
        return 'uid=0(root) gid=0(root) groups=0(root)'

    def do_exit(self, args=None):
        ''' Returns an exit signal to the caller. '''
        if args is None:
            args = []
        raise error.ClientCommandExit()

    def do_rm(self, args=None):
        ''' Stub `rm`. '''
        if args is None:
            args = []
        return

    def do_cp(self, args=None):
        ''' Stub `cp`. '''
        if args is None:
            args = []
        return

    def do_cd(self, args=None):
        ''' Stub `cd`. '''
        if args is None:
            args = []
        return

    def do_wget(self, args=None):
        ''' Stub `wget`. '''
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
        process_list.append('PID   Uid    VmSize    Stat    Command\r\n')
        process_list.append('  1   root      404     S      init')
        return ''.join(process_list)


    def handle(self, command):
        ''' Dispatches the input command to the relevant handler. '''
        args = re.split(r'\s+', command)
        if len(args) < 1:
            return

        # If present, remove full path prefix from command.
        cmd = args[0].split('/')[-1]
        args.pop(0)

        # Decode encoded characters where required.
        decoded_args = []
        for arg in args:
            if "\\x" in arg:
                try:
                    decoded_args.append(arg.replace("\\x", "").decode("hex"))
                except (TypeError, ValueError) as _:
                    decoded_args.append(arg)
            else:
                decoded_args.append(arg)

        # Attempt to locate a command handler for the read command.
        try:
            ref = getattr(self, "do_{}".format(cmd))
        except AttributeError:
            if len(cmd) < 1:
                return ''
            return "sh: {}: command not found\r\n".format(cmd)

        # Call found handler with provided arguments, and write response back
        # to socket.
        result = ref(decoded_args)
        if result:
            return '{}\r\n'.format(result.strip())
        else:
            return '\r\n'
