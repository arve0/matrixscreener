from matrixscreener.cam import *
import pytest

class EchoSocket:
    "Dummy echo socket for mocking."
    msg = ''

    def send(self, msg):
        self.msg = msg
        return len(msg)

    def recv(self, buffer_size):
        return self.msg[0:buffer_size]

    def connect(self, where):
        pass

# TEST
#- key (here cli) overrided if defined several times
#- prefix added
#- types (integer, float) should be converted to strings
def test_echo(monkeypatch):
    "Prefix + command sent should be same as echoed socket message."
    # mock socket
    monkeypatch.setattr("socket.socket", EchoSocket)

    # setup cam
    cam = CAM()
    cam.connect()

    cmd = [('cli', 'custom'), ('cmd', 'enableall'), ('value', 'true'),
           ('integer', 1234), ('float', 0.00234)]

    echoed = bytes_as_dict(cam.send(cmd))
    sent = tuples_as_dict(cam.prefix + cmd)

    assert sent == echoed
