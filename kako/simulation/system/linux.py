import pprint

from kako.simulation.server import error


class CommandInterpreter(object):
    ''' Implements commands for an embedded BusyBox system (Linux). '''
    version = 'BusyBox v1.19.3 (2013-11-01 10:10:26 CST)'

    def do_echo(self, args=[]):
        ''' Returns the input as provided. '''
        return ' '.join(args).strip()

    def do_id(self, args=[]):
        ''' Returns `id` command output. '''
        return 'uid=0(root) gid=0(root) groups=0(root)'

    def do_exit(self, args=[]):
        ''' Returns an exit signal to the caller. '''
        raise error.ClientCommandExit()

    def do_busybox(self, args=[]):
        ''' Wrapper the handle() method to handle BusyBox applets. '''
        if len(args) > 0:
            return self.handle(' '.join(args))
        else:
            return self.version

    def handle(self, command):
        ''' Dispatches the input command to the relevant handler. '''
        args = command.split(' ')  # TODO: Regex for one or more space(s).
        if len(args) < 1:
            return

        # If it exists, Remove full path prefix from command.
        cmd = args[0].split('/')[-1]
        args.pop(0)

        try:
            ref = getattr(self, "do_{}".format(cmd))
            return '{}\r\n'.format(ref(args).strip())
        except AttributeError:
            if len(cmd) < 1:
                return ''
            return "sh: {}: command not found\r\n".format(cmd)
