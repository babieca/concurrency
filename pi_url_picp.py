#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
import math
import random
import gevent
import multiprocessing
import logging
from decimal import *
from blocking_socket import blocking_socket
from utils import CHUNK_SIZE, POOL_SIZE, DECIMAL_PLACES, getArguments, numdiff

logger = logging.getLogger('standard')

def ramanuja(child_conn):

    getcontext().prec = DECIMAL_PLACES

    k = 0
    total = 0
    factor = Decimal(2) * Decimal(2).sqrt() / Decimal(9801)

    child_conn.send(None)
    
    while True:
        if child_conn.poll():   # if no data, do not block
            if child_conn.recv() is None:
                r = Decimal(1) / total if total != 0 else 0
                return r
        else:
            num = math.factorial(4 * k) * (1103 + (26390 * k))
            den = math.factorial(k) ** 4 * 396 ** (4 * k)
            term = factor * Decimal(num) / Decimal(den)
            total += term
            k += 1


def main(addr='127.0.0.1', port=8080, max_open_sockets=2000, delay=0.0, random_delay=False, numreq=1):

    pool_fd = [max_open_sockets] * (numreq // max_open_sockets)
    mod = numreq % max_open_sockets
    if mod != 0:
        pool_fd.append(mod)

    start = time.time()

    pool = multiprocessing.Pool(processes=POOL_SIZE)
    parent_conn, child_conn = multiprocessing.Pipe()
    proc1 = pool.apply_async(func=ramanuja, args=(child_conn,))

    _ = parent_conn.recv()      # wait for the process to be ready

    g2 = [None]
    for i, group in enumerate(pool_fd):
        g2 = []
        for j in range(group):
            delay = round(random.random(), 2) if random_delay else delay
            path = 'pool-{}-of-{}/req-{}-of-{}/?delay={}'.format(i, len(pool_fd), j, group, delay)
            g2.append(gevent.spawn(blocking_socket, addr, port, path))
        gevent.joinall(g2)

    parent_conn.send(None)

    pool.close()
    pool.join()

    elapsed = time.time() - start

    est_pi = proc1.get()
    real_pi = g2[0].value
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
