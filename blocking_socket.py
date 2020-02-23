import socket
import logging
from utils import CHUNK_SIZE

logger = logging.getLogger('standard')


def blocking_socket(addr='127.0.0.1', port=8080, path='/'):
    sock = socket.socket()
    sock.connect((addr, port))

    resp = None
    buf = []
    request = 'GET {} HTTP/1.0\r\n\r\n'.format(path)
    try:
        sock.send(request.encode())
    except:
        pass
    else:
        while True:
            try:
                chunk = sock.recv(CHUNK_SIZE)
            except:
                buf = None
                break
            else:
                if chunk:
                    buf.append(chunk)
                else:
                    break

        if buf and isinstance(buf, list):
            try:
                raw_resp = b''.join(buf)
                resp = raw_resp.decode()
                if resp and resp.find('\r\n\r\n'):
                    resp = resp.split('\r\n\r\n')[1].strip()
            except:
                resp = None

    sock.close()

    return resp
