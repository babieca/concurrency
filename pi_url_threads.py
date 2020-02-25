import sys
import time
import multiprocessing
from multiprocessing.pool import ThreadPool
import random
import logging
from utils import CHUNK_SIZE, POOL_SIZE, getArguments, numdiff
from ramanujan import ramanuja
from blocking_socket import blocking_socket

logger = logging.getLogger('standard')


def main(addr='127.0.0.1', port=8080, max_open_sockets=2000, delay=0.0, random_delay=False, numreq=1):

    manager = multiprocessing.Manager()
    queue = manager.Queue()
    pool = ThreadPool(processes=POOL_SIZE)

    pool_fd = [max_open_sockets] * (numreq // max_open_sockets)
    mod = numreq % max_open_sockets
    if mod != 0:
        pool_fd.append(mod)

    start = time.time()

    thread1 = pool.apply_async(func=ramanuja, args=(queue,))
    thread2 = []
    for i, group in enumerate(pool_fd):
        thread2 = []
        for j in range(group):
            delay = round(random.random(), 2) if random_delay else delay
            path = 'pool-{}-of-{}/req-{}-of-{}/?delay={}'.format(i, len(pool_fd), j, group, delay)
            thread2.append(pool.apply_async(func=blocking_socket, args=(addr, port, path)))
        [t.wait() for t in thread2]

    queue.put(None)

    pool.close()
    pool.join()

    elapsed = time.time() - start

    real_pi = thread2[0].get()
    est_pi = thread1.get()

    equal_digits = numdiff(est_pi, real_pi)

    return elapsed, equal_digits


if __name__ == '__main__':
    args = getArguments()

    try:
        elapsed, equal_digits = main(addr=args.addr, port=args.port, max_open_sockets=args.limit, delay=args.delay, random_delay=args.random, numreq=args.numreq)
        logger.info("Total Req.={:,} | Time={:,.6f} sec, | equal digits={:,}".format(args.numreq, elapsed, equal_digits))
    except KeyboardInterrupt:
        pass

    sys.exit(0)
