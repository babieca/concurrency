import asyncio
import socket
import errno
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from urllib.parse import urlparse
import logging
from utils import CHUNK_SIZE, readpi1m, getArguments, real_pi

logger = logging.getLogger('standard')


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = BytesIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message


async def handle_client(loop, client, delay=0):
    try:
        rawrequest = await loop.sock_recv(client, CHUNK_SIZE)
    except:
        pass
    else:
        if rawrequest:
            request = HTTPRequest(rawrequest)

            req = request.raw_requestline.decode('utf-8').replace('\r\n', '')
            # req_headers = request.headers.as_string().replace('\n', ' ')

            logme = "[ OK << ] {}".format(req)
            logger.info(logme)

            query = urlparse(request.path).query
            query_components = dict(qc.split("=") for qc in query.split("&") if "=" in qc)
            await asyncio.sleep(float(query_components.get('delay', delay)))

            res_headers = "HTTP/1.1 200 OK\r\nContent-Type: text/plain"
            data = res_headers + '\r\n\r\n' + real_pi

            try:
                await loop.sock_sendall(client, data.strip().encode('utf8'))
                logme = "[ OK >> ] {}".format(req)
            except:
                logme = "[ Error >> ] {}".format(req)
            logger.info(logme)
    client.close()


async def async_server(loop, sock, delay=0):
    try:
        while True:
            client, _ = await loop.sock_accept(sock=sock)
            loop.create_task(handle_client(loop=loop, client=client, delay=delay))
    except KeyboardInterrupt:
        return


def server(addr='localhost', port=8080, delay=0):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((addr, port))
    sock.listen(8)
    sock.setblocking(False)

    loop = asyncio.get_event_loop()

    logger.info("Server listening on {}:{}".format(addr, port))

    loop.run_until_complete(async_server(loop=loop, sock=sock, delay=delay))


if __name__ == "__main__":

    args = getArguments()

    server(addr=args.addr, port=args.port, delay=args.delay)
