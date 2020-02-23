#!/usr/bin/env python
"""Computes an estimate of pi.

Algorithm due to Srinivasa Ramanujan, from
http://en.wikipedia.org/wiki/Pi
"""
import sys
import math
import time
import logging
import argparse
from decimal import *
import multiprocessing
from utils import checkpi, DECIMAL_PLACES

logger = logging.getLogger('standard')


def ramanuja(in_queue, est_pi=None):

    getcontext().prec = DECIMAL_PLACES

    k = 0
    total = 0
    factor = Decimal(2) * Decimal(2).sqrt() / Decimal(9801)

    while True:
        if not in_queue.empty():
            r = Decimal(1) / total if total != 0 else 0
            if isinstance(est_pi, list):
                est_pi.append(r)
            return r

        num = math.factorial(4 * k) * (1103 + (26390 * k))
        den = math.factorial(k) ** 4 * 396 ** (4 * k)
        term = factor * Decimal(num) / Decimal(den)
        total += term
        k += 1


def main(sleep=3):

    manager = multiprocessing.Manager()
    queue = manager.Queue()
    pool = multiprocessing.Pool()

    proc = pool.apply_async(func=ramanuja, args=(queue, ))

    time.sleep(sleep)

    queue.put(None)

    pool.close()
    pool.join()

    est_pi = proc.get()
    diff_digits = checkpi(est_pi)

    return diff_digits


def getArguments():
    parser = argparse.ArgumentParser(description='Simple non-blocking http server')
    parser.add_argument('-t', '--time', type=float, default=3, help='Time to process')
    return parser.parse_args()


if __name__ == "__main__":
    args = getArguments()

    start = time.time()
    est_pi = main(sleep=args.time)
    elapsed = time.time() - start

    logger.info("Time={:,.6f} sec, | est. pi={:,}".format(elapsed, est_pi))

    sys.exit(0)
