#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all(socket=False)
import sys
import time
import math
import random
import gevent
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
            print("K values is {}".format(k))
            num = math.factorial(4 * k) * (1103 + (26390 * k))
            den = math.factorial(k) ** 4 * 396 ** (4 * k)
            term = factor * Decimal(num) / Decimal(den)
            total += term
            k += 1
            gevent.sleep(0)

    except gevent.GreenletExit:
        r = Decimal(1) / total if total != 0 else 0
        print(r)
        return (r)



def main(addr='127.0.0.1', port=8080, max_open_sockets=2000, delay=0.0, random_delay=False, numreq=1):

    start = time.time()


    pool_fd = [max_open_sockets] * (numreq // max_open_sockets)
    mod = numreq % max_open_sockets
    if mod != 0:
        pool_fd.append(mod)

    print(1)
    g1 = gevent.spawn(ramanuja)
    print(2)

    for i, pool in enumerate(pool_fd):
        g2 = []
        print("in first loop")
        for j in range(pool):
            print("in second loop")
            delay = round(random.random(), 2) if random_delay else delay
            path = 'pool-{}-of-{}/req-{}-of-{}/?delay={}'.format(i, len(pool_fd), j, pool, delay)
            g2.append(gevent.spawn(blocking_socket, addr, port, path))
            print("after spawn blocking socket")
        print("before join all")
        gevent.joinall(g2)
        print("after join all")
    print(3)

    g1.kill()
    print(4)

    elapsed = time.time() - start
    est_pi = g1.value
    print(5)
    real_pi = g2[0].value
    print(6)
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
