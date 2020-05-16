import socket
import select
import time
import logging
from .server import Session


class PortMappingSession(Session):

    def __init__(self, address, poll_interval=0.5, timeout=None, disable_nagle_algorithm=False, buffer_size=2048):
        super(PortMappingSession, self).__init__()
        self.address = address
        self.poll_interval = poll_interval
        self.timeout = timeout
        self.disable_nagle_algorithm = disable_nagle_algorithm
        self.buffer_size = buffer_size

    def setup_socket(self, sock):
        if self.disable_nagle_algorithm:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

    def send_hook(self, data: bytes) -> bytes:
        logging.debug(f"send://{data}")
        return data

    def recv_hook(self, data: bytes) -> bytes:
        logging.debug(f"recv://{data}")
        return data

    def handle(self, request: socket.socket, client_address):
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as sock:
            sock.connect(self.address)
            logging.debug(f"session-<{self.session_id}> timeout={self.timeout}")
            logging.debug(f"session-<{self.session_id}> disable_nagle_algorithm={self.disable_nagle_algorithm}")
            self.setup_socket(sock)
            self.setup_socket(request)
            stop = False
            timeout_integral = time.time()
            while not stop:
                rfds, _, _ = select.select([sock, request], [], [], self.poll_interval)
                # There are no timeout exceptions in non-blocking mode. Use a timeout argument to select(),
                # and detect the case where select() returns without any ready sockets.
                logging.debug(f"session-<{self.session_id}> ready={len(rfds)}")
                if sock in rfds:
                    timeout_integral = time.time()
                    data = sock.recv(self.buffer_size)
                    if not data:
                        stop = True
                    request.sendall(self.recv_hook(data))

                if request in rfds:
                    timeout_integral = time.time()
                    data = request.recv(self.buffer_size)
                    if not data:
                        stop = True
                    sock.sendall(self.send_hook(data))

                if len(rfds) == 0 and self.timeout and (time.time() - timeout_integral) > self.timeout:
                    raise TimeoutError(f"Port mapping {client_address} <> {self.address} timeout.")

            logging.info(f"port mapping {client_address} <> {self.address} exit")
