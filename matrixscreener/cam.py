from time import sleep
from collections import OrderedDict


def tuples_as_bytes(cmds):
    """Format list of tuples to CAM message with format /key:val.

    Parameters
    ----------
    cmds : list of tuples
        List of commands as tuples.
        Example: [('cmd', 'val'), ('cmd2', 'val2')]

    Returns
    -------
    bytes
        Sequence of /key:val.
    """
    cmds = OrderedDict(cmds) # override equal keys
    tmp = []
    for key,val in cmds.items():
        key = str(key)
        val = str(val)
        tmp.append('/' + key + ':' + val)
    return ' '.join(tmp).encode()


def tuples_as_dict(_list):
    """Translate a list of tuples to OrderedDict with key and val
    as strings.

    Parameters
    ----------
    _list : list of tuples
        Example: [('cmd', 'val'), ('cmd2', 'val2')]

    Returns
    -------
    collections.OrderedDict
    """
    _dict = OrderedDict()
    for key,val in _list:
        key = str(key)
        val = str(val)
        _dict[key] = val
    return _dict


def bytes_as_dict(msg):
    """Parse CAM message to OrderedDict based on format /key:val.

    Parameters
    ----------
    command : bytes
        Sequence of /key:val.

    Returns
    -------
    collections.OrderedDict
        With /key:val => dict[key] = val.
    """
    # decode bytes, assume '/' in start
    cmd_strings = msg.decode()[1:].split(r' /')
    cmds = OrderedDict()
    for cmd in cmd_strings:
        key, val = cmd.split(':')
        cmds[key] = val
    return cmds



class CAM:
    "Driver for LASAF Computer Assisted Microscopy."

    def __init__(self, host='127.0.0.1', port=8895):
        self.host = host
        self.port = port
        # prefix for all commands
        self.prefix = [('cli', 'python-matrixscreener'),
                       ('app', 'matrix')]
        self.buffer_size = 1024
        self.delay = 50e-3 # wait 50ms after sending commands
        self.connected = False
        self.socket = None


    def connect(self):
        "Connects to LASAF through a CAM-socket."
        import socket
        self.socket = socket.socket()
        self.socket.connect((self.host, self.port))
        sleep(self.delay) # wait for response
        self.last_msg = self.socket.recv(self.buffer_size) # receive welcome message
        self.connected = True


    def send(self, commands):
        """Send commands to LASAF through CAM-socket.

        Paramenters
        -----------
        commands : list of tuples
            Commands as a list of tuples. matrixscreener.CMD_PREFIX is
            prepended to commands.
            Example: [('cmd', 'enableall'), ('value', 'true')]

        Returns
        -------
        bytes
            Response message from LASAF.
        """
        self.socket.send(tuples_as_bytes(self.prefix + commands))
        sleep(self.delay)
        return self.socket.recv(self.buffer_size)


    # convinience functions for commands
    def start_scan(self):
        "Starts the matrix scan."
        cmd = [('cmd', 'startscan')]
        return self.send(cmd)


    def stop_scan(self):
        "Stops the matrix scan."
        cmd = [('cmd', 'stopscan')]
        return self.send(cmd)


    def pause_scan(self):
        "Pauses the matrix scan."
        cmd = [('cmd', 'pausescan')]
        return self.send(cmd)


    def enable(self, slide=1, wellx=1, welly=1,
               fieldx=1, fieldy=1, value='true'):
        "Enable a given scan field."
        cmd = [
            ('slide', str(slide)),
            ('wellx', str(wellx)),
            ('welly', str(welly)),
            ('fieldx', str(fieldx)),
            ('fieldy', str(fieldy)),
            ('value', str(value))
        ]
        return self.send(cmd)


    def disable(self, **kwargs):
        "Shorthand for CAM.enable(value='false')."
        return self.enable(value='false', **kwargs)


    def enable_all(self):
        "Enable all scan fields."
        cmd = [('cmd', 'enableall'), ('value', 'true')]
        return self.send(cmd)


    def disable_all(self):
        "Disable all scan fields."
        cmd = [('cmd', 'enableall'), ('value', 'false')]
        return self.send(cmd)


    def save_template(self, filename="{ScanningTemplate}matrixscreener.xml"):
        "Save scanning template to filename."
        cmd = [
            ('sys', '1'),
            ('cmd', 'save'),
            ('fil', str(filename))
        ]
        return self.send(cmd)


    def load_template(self, filename="{ScanningTemplate}matrixscreener.xml"):
        """Load scanning template from filename. Template needs to exist
        in database, otherwise it will not load.
        """
        cmd = [
            ('sys', '1'),
            ('cmd', 'load'),
            ('fil', str(filename))
        ]
        return self.send(cmd)


    def get_information(self, about='stage'):
        "Get information about given keyword. Defaults to stage."
        cmd = [
            ('cmd', 'getinfo'),
            ('dev', str(about))
        ]
        return self.send(cmd)
