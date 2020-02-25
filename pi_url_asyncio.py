import sys
import math
import time
import random
import logging
import asyncio
import multiprocessing
import concurrent.futures
from decimal import *
from blocking_socket import blocking_socket
from utils import CHUNK_SIZE, getArguments, numdiff, DECIMAL_PLACES

logger = logging.getLogger('standard')


async def ramanuja(in_queue, est_pi):

    getcontext().prec = DECIMAL_PLACES

    k = 0
    total = 0
    factor = Decimal(2) * Decimal(2).sqrt() / Decimal(9801)

    while True:
        print(k)
        if not in_queue.empty():
            print("K values is {}".format(k))
            est_pi.append(Decimal(1) / total if total != 0 else 0)
            return

        num = math.factorial(4 * k) * (1103 + (26390 * k))
        den = math.factorial(k) ** 4 * 396 ** (4 * k)
        term = factor * Decimal(num) / Decimal(den)
        total += term
        k += 1


async def main(addr='127.0.0.1', port=8080, max_open_sockets=2000, delay=0.0, random_delay=False, numreq=1):

    resps = []
    manager = multiprocessing.Manager()
    queue = manager.Queue()

    pr_executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
    th_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    pool_fd = [max_open_sockets] * (numreq // max_open_sockets)
    mod = numreq % max_open_sockets
    if mod != 0:
        pool_fd.append(mod)

    loop = asyncio.get_event_loop()

    start = time.time()

    future = loop.run_in_executor(pr_executor, ramanuja, queue, resps)
    asyncio.ensure_future(coro_or_future=future, loop=loop)

    tasks = []
    results = []
    for i, pool in enumerate(pool_fd):
        for j in range(pool):
            delay = round(random.random(), 2) if random_delay else delay
            path = 'pool-{}-of-{}/req-{}-of-{}/?delay={}'.format(i, len(pool_fd), j, pool, delay)
            tasks.append(loop.run_in_executor(th_executor, blocking_socket, addr, port, path))
        completed, pending = await asyncio.wait(tasks)
        for t in completed:
            results.append(t.result())

    print(1)
    queue.put(None)
    print(2)
    print(resps)
    print(3)
    est_pi = 3.1415
    print(est_pi)
    print(6)
    real_pi = results[0] if results else 0

    elapsed = time.time() - start

    equal_digits = numdiff(est_pi, real_pi)

    return elapsed, equal_digits


if __name__ == '__main__':

    args = getArguments()

    event_loop = asyncio.get_event_loop()

    try:
        w = asyncio.wait([main(addr=args.addr, port=args.port, max_open_sockets=args.limit, delay=args.delay, random_delay=args.random, numreq=args.numreq)])
        completed, pending = event_loop.run_until_complete(w)
        elapsed, equal_digits = next(fut.result() for fut in completed)
        logger.info("Total Req.={:,} | Time={:,.6f} sec, | equal digits={:,}".format(args.numreq, elapsed, equal_digits))
    finally:
        event_loop.close()

    sys.exit(0)