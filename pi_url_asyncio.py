import time
import math
from decimal import *
import aiohttp
import asyncio
from contextlib import suppress
from concurrent.futures import ProcessPoolExecutor

getcontext().prec = 100_000


async def ramanuja(est_pi, iterations):

    k = 0
    factor = Decimal(2) * Decimal(2).sqrt() / Decimal(9801)
    total = 0
    while True:
        num = math.factorial(4 * k) * (1103 + (26390 * k))
        den = math.factorial(k) ** 4 * 396 ** (4 * k)
        term = factor * Decimal(num) / Decimal(den)
        total += term
        k += 1

        est_pi.append(Decimal(1) / total if total != 0 else 0)
        iterations.append(k - 1 if k > 0 else 0)


def on_done(task, est_pi, iterations):
    if task.cancelled():
        print("incomplete")
    else:
        print("complete")


async def fetch(session, url):

    async with session.get(url) as resp:
        if resp.status != 200:
            resp.raise_for_status()
        return await resp.text()


async def fetch_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results


async def main():
    target = 'http://localhost:8080/{}'
    numreq = 10
    est_pi = []
    iterations = []

    urls = [target.format(i) for i in range(numreq)]

    start = time.time()

    #task = asyncio.Task(ramanuja(est_pi=est_pi, iterations=iterations))
    #task.add_done_callback(lambda t: on_done(t, est_pi, iterations))

    async with aiohttp.ClientSession() as session:
        content = await fetch_all(session, urls)

    # task.cancel()
    # with suppress(asyncio.CancelledError):
    #     await task

    elapsed = time.time() - start
    print("Time = {:,.6f} sec, | diff. digit = {:,}".format(elapsed, 0))

if __name__ == '__main__':
    executor = ProcessPoolExecutor(2)
    loop = asyncio.get_event_loop()
    future1 = asyncio.ensure_future(loop.run_in_executor(executor, main))
    #baa = asyncio.ensure_future(loop.run_in_executor(executor, say_baa))

    loop.run_until_complete(future1)
    #asyncio.run(main())
