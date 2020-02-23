#!/usr/bin/env python
"""Computes an estimate of pi.

Algorithm due to Srinivasa Ramanujan, from
http://en.wikipedia.org/wiki/Pi
"""

import math
import argparse
from decimal import *
import time


def ramanujan():
    k = 0
    factor = Decimal(2 * math.sqrt(2) / 9801)
    total = Decimal(0)
    while True:
        total = yield total
        if total is None:
            break
        num = math.factorial(4 * k) * (1103 + 26390 * k)
        den = math.factorial(k) ** 4 * 396 ** (4 * k)
        term = factor * Decimal(num) / Decimal(den)
        total += term
        k += 1
    return total


def controller():

    while True:
        result = yield from ramanujan()
        if result is None:
            break


def getArguments():
    parser = argparse.ArgumentParser(description='Simple non-blocking http server')
    parser.add_argument('-p', '--prec', type=int, default=28, help='Precision decimal numbers')
    parser.add_argument('-n', type=int, default=10, help='Number of iterations')
    return parser.parse_args()


if __name__ == "__main__":

    args = getArguments()

    getcontext().prec = args.prec

    hub = controller()
    next(hub)
    counter = 0

    total = Decimal(0)
    start = time.time()
    while True:
        if counter >= args.n:
            try:
                hub.send(None)
            except StopIteration:
                break
        else:
            total = hub.send(total)
            counter += 1
    end = time.time()

    est_pi = Decimal(1) / total if total != 0 else 0

    print("PI={:,.{prec}f}".format(est_pi, prec=args.prec))
    print("Time={:,.6f}sec.".format(end-start))
