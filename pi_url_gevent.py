#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()
import sys
import time
import math
import random
import gevent
from gevent.threadpool import ThreadPool
import logging
from decimal import *
from blocking_socket import blocking_socket
from utils import CHUNK_SIZE, DECIMAL_PLACES, getArguments, numdiff

logger = logging.getLogger('standard')

def ramanuja():

    getcontext().prec = DECIMAL_PLACES

    k = 0
    total = 0
    factor = Decimal(2) * Decimal(2).sqrt() / Decimal(9801)

    try:
        while True:
            num = math.factorial(4 * k) * (1103 + (26390 * k))
            den = math.factorial(k) ** 4 * 396 ** (4 * k)
            term = factor * Decimal(num) / Decimal(den)
            total += term
            gevent.sleep(0.001)
            k += 1

    except gevent.GreenletExit:
        return Decimal(1) / total if total != 0 else 0


def main(addr='127.0.0.1', port=8080, max_open_sockets=2000, delay=0.0, random_delay=False, numreq=1):

    pool_fd = [max_open_sockets] * (numreq // max_open_sockets)
    mod = numreq % max_open_sockets
    if mod != 0:
        pool_fd.append(mod)

    start = time.time()

    g1 = gevent.spawn(ramanuja)

    for i, pool in enumerate(pool_fd):
        g2 = []
        for j in range(pool):
            delay = round(random.random(), 2) if random_delay else delay
            path = 'pool-{}-of-{}/req-{}-of-{}/?delay={}'.format(i, len(pool_fd), j, pool, delay)
            g2.append(gevent.spawn(blocking_socket, addr, port, path))
        gevent.joinall(g2)

    g1.kill()

    elapsed = time.time() - start
    est_pi = g1.value
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
