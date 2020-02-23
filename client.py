import socket
import time
import argparse

CHUNKS = 1024


def sock(addr='127.0.0.1', port=8080, path='/'):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((addr, port))
    s.send(('GET {} HTTP/1.0\r\n\r\n'.format(path)).encode())

    buf = []
    while True:
        chunk = s.recv(CHUNKS)
        if not chunk:
            break
        buf.append(chunk)
    s.close()

    return (b''.join(buf)).decode().split('\r\n\r\n')


def fetchurl(resps, url='127.0.0.1', port=8080, delay=0):

    path = '/?delay={}'.format(delay) if delay else '/'

    init = time.time()
    start = time.time()
    header, body = sock(addr=url, port=port, path=path)
    end = time.time()
    status_code = header.split('\r\n')[0]
    req_time = end - start
    total_time = end - init

    key = sorted(resps.keys())[-1] + 1 if resps else 0
    resps[key] = {'status_code': status_code, 'req_time': req_time, 'total_time': total_time, 'header': header, 'body': body}
    return resps


def getArguments():
    parser = argparse.ArgumentParser(description='Simple non-blocking http server')
    parser.add_argument('-u', '--url', type=str, default='127.0.0.1', help='Target url')
    parser.add_argument('-p', '--port', type=int, default=8080, help='Target port number')
    parser.add_argument('-n', type=int, default=1, help='Number of requests')
    parser.add_argument('-d', '--delay', type=float, default=0, help='delay for the server to respond')
    return parser.parse_args()


if __name__ == "__main__":

    args = getArguments()

    resps = {}
    for i in range(args.n):
        fetchurl(resps=resps, url=args.url, port=args.port, delay=args.delay)

    for i, resp in resps.items():
        status_code = resp.get('status_code', 0)
        total_time = resp.get('total_time', 0)
        req_time = resp.get('req_time', 0)
        print("[{:{},}] {}. Times: {:.6f} req. | {:.6f} tot.".format(
            i, len(str(args.n)), status_code, req_time, total_time))