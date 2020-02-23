#!/usr/bin/env python
import grequests
import sys
import time

N = int(sys.argv[1])
urls = ['http://127.0.0.1:8080'] * N

reqs = (grequests.get(url) for url in urls)

start = time.time()
resps = grequests.map(reqs)
elapsed = time.time() - start

# 'apparent_encoding', 'close', 'connection', 'content', 'cookies', 'elapsed', 'encoding', 'headers', 'history',
# 'is_permanent_redirect', 'is_redirect', 'iter_content', 'iter_lines', 'json', 'links', 'next', 'ok',
# 'raise_for_status', 'raw', 'reason', 'request', 'status_code', 'text', 'url']

for i, resp in enumerate(resps):
    status_code = resp.status_code
    text = resp.text
    req_time = resp.elapsed.total_seconds()
    print("[{:{},}] {}. Times: {:.6f} req. | {:.6f} tot. ".format(i, len(str(N)), status_code, req_time, elapsed))
