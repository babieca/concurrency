#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
import random
import logging
import multiprocessing
from multiprocessing import Pool as ProcPool
from ramanujan import ramanuja
from non_blocking_socket import non_blocking_socket, eventLoop
from utils import CHUNK_SIZE, getArguments, numdiff

logger = logging.getLogger('standard')


def main(addr='127.0.0.1', port=8080, max_open_sockets=2000, delay=0.0, random_delay=False, numreq=1):

    resps = []
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    procpool = ProcPool(processes=4)

    start = time.time()

    process = procpool.apply_async(func=ramanuja, args=(queue, ))

    pool_fd = [max_open_sockets] * (numreq // max_open_sockets)
    mod = numreq % max_open_sockets
    if mod != 0:
        pool_fd.append(mod)

    for i, pool in enumerate(pool_fd):
        for j in range(pool):
            delay = round(random.random(), 2) if random_delay else delay
            path = 'pool-{}-of-{}/req-{}-of-{}/?delay={}'.format(i, len(pool_fd), j, pool, delay)
            eventLoop.add_task(non_blocking_socket(result=resps, addr=addr, port=port, path=path))
        eventLoop.run()

    queue.put(None)

    procpool.close()
    procpool.join()

    elapsed = time.time() - start

    est_pi = process.get()
    real_pi = resps[0]

    equal_digits = numdiff(est_pi, real_pi)

    return elapsed, equal_digits


if __name__ == '__main__':

    args = getArguments()

    try:
        elapsed, equal_digits = main(addr=args.addr, port=args.port, max_open_sockets=args.limit, delay=args.delay, random_delay=args.random, numreq=args.numreq)
        logger.info("Total Req.={:,} | Time={:,.6f} sec, | diff. digit={:,}".format(args.numreq, elapsed, equal_digits))

    except KeyboardInterrupt:
        pass

    sys.exit(0)
