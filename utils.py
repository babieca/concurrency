import logging
import argparse
from decimal import *
from datetime import datetime

POOL_SIZE = 8
CHUNK_SIZE = 65535
DECIMAL_PLACES = 100_000
filename = './pi1m.txt'


class MyFormatter(logging.Formatter):

    converter = datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):

        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


logger = logging.getLogger('standard')
logger.setLevel(logging.INFO)

console = logging.StreamHandler()
logger.addHandler(console)

# fmt='%(asctime)s [%(filename)s:%(lineno)d] - %(message)s'
formatter = MyFormatter(fmt='%(asctime)s - %(message)s', datefmt='%Y-%m-%d,%H:%M:%S.%f')
console.setFormatter(formatter)


def readpi1m():
    with open(filename, 'r') as f:
        content = f.read().replace('\n', '').strip()
    return content

real_pi = readpi1m()


def checkpi(est_pi):
    return numdiff(est_pi, real_pi)


def numdiff(num1, num2):

    num1_str = str(num1)
    num2_str = str(num2)

    maxval = min(DECIMAL_PLACES, len(num1_str), len(num2_str))
    equal_digits = next((i for i in range(maxval) if num1_str[i] != num2_str[i]), maxval)

    return equal_digits


def getArguments():
    parser = argparse.ArgumentParser(description='Simple non-blocking http server')
    parser.add_argument('-a', '--addr', type=str, default='127.0.0.1', help='remote ip address')

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('-d', '--delay', type=float, default=0, help='delay response')
    group.add_argument('-r', '--random', type=bool, default=False, help='random delay')

    parser.add_argument('-p', '--port', type=int, default=8080, help='remote port')
    parser.add_argument('-l', '--limit', type=int, default=2000, help='max. number of open file descriptors')
    parser.add_argument('-n', '--numreq', type=int, default=20, help='number of requests')
    return parser.parse_args()
