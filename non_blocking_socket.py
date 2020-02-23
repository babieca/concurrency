import sys
import time
import socket
import errno
import random
import logging
import resource
from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
from utils import getArguments, CHUNK_SIZE

logger = logging.getLogger('standard')

selector = DefaultSelector()

class Future:
    def __init__(self):
        self.callback = None

    def resolve(self):
        self.callback()

    def __await__(self):
        yield self


class Task:
    def __init__(self, gen, eventloop):
        self.gen = gen
        self.eventloop = eventloop
        self.step()

    def step(self):
        try:
            fut = self.gen.send(None)
        except StopIteration as e:
            self.eventloop.n_task -= 1
        else:
            fut.callback = self.step


class EventLoop:
    def __init__(self):
        self.n_task = 0

    def add_task(self, generator):
        self.n_task += 1
        Task(generator, self)

    def run(self):
        while self.n_task > 0:
            events = selector.select()
            for event, mask in events:
                fut = event.data
                fut.resolve()


async def async_await(s, event):
    fut = Future()
    selector.register(s.fileno(), event, data=fut)
    await fut
    selector.unregister(s.fileno())


async def non_blocking_socket(result, addr='127.0.0.1', port=8080, path='/'):
    sock = socket.socket()
    sock.settimeout(10)
    sock.connect((addr, port))
    sock.setblocking(0)
    # sock.setblocking(False)
    # try:
    #     sock.connect((addr, port))
    # except BlockingIOError as e:
    #     pass
    # except:
    #     sock.close()
    #     return

    await async_await(sock, EVENT_WRITE)

    resp = None
    buf = []
    req = 'GET {} HTTP/1.0'.format(path)

    try:
        sock.send((req + '\r\n\r\n').encode())
        logme = "[ OK >> ] {}".format(req)
        logger.info(logme)
    except:
        logme = "[ Error >> ] {}".format(req)
        logger.info(logme)
    else:

        while True:
            await async_await(sock, EVENT_READ)
            try:
                chunk = sock.recv(CHUNK_SIZE)
            except:
                buf = None
                logme = "[ Error << ] {}".format(req)
                break
            else:
                if chunk:
                    buf.append(chunk)
                else:
                    logme = "[ OK << ] {}".format(req)
                    break

        if buf and isinstance(buf, list):
            try:
                raw_resp = b''.join(buf)
                resp = raw_resp.decode()
                if resp and resp.find('\r\n\r\n'):
                    resp = resp.split('\r\n\r\n')[1].strip()
                    result.append(resp)
            except:
                logme = "[ Error << ] {}".format(req)
                resp = None

    sock.close()

    logger.info(logme)
    return resp


eventLoop = EventLoop()

if __name__ == '__main__':
    args = getArguments()
    delay = random.random() if args.random else args.delay

    start = time.time()

    result = []

    soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)

    numreq = args.numreq
    max_open_sockets = args.limit
    pool_requests = [max_open_sockets] * (numreq // max_open_sockets)
    mod = numreq % max_open_sockets
    if mod != 0:
        pool_requests.append(mod)

    for i, pool in enumerate(pool_requests):
        logging.info("Sending block of {} sockets".format(pool))
        for j in range(pool):
            path = 'pool-{}-of-{}/req-{}-of-{}/?delay={}'.format(i, len(pool_requests), j, pool, delay)
            eventLoop.add_task(
                non_blocking_socket(result=result, addr=args.addr, port=args.port, path=path))
        eventLoop.run()

    logger.info('{:,.6f} sec'.format(time.time() - start))

    sys.exit(0)

