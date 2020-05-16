import uuid
import selectors
import logging
import threading
import socket


_ServerSelector = selectors.PollSelector


def shutdown_request(request):
    try:
        request.shutdown(socket.SHUT_WR)
    except OSError:
        pass  # some platforms may raise ENOTCONN here
    close_request(request)


def close_request(request):
    request.close()


def handle_error(error, client_address):
    logging.error("-" * 40)
    logging.error(f"Exception happened during processing of request from {client_address}")
    logging.exception(error)
    logging.error("-" * 40)


class Session:

    def __init__(self):
        self.session_id = None

    def start(self, request, client_address):
        try:
            logging.info(f"session-<{self.session_id}> start")
            self.handle(request, client_address)
        except BaseException as error:
            logging.error(f"session-<{self.session_id}> handle error")
            handle_error(error, client_address)
        finally:
            shutdown_request(request)
            logging.info(f"session-<{self.session_id}> exit")

    def handle(self, request, client_address):
        raise NotImplementedError()


class Server:

    def __init__(self, address, request_queue_size, session_type: type, *session_args, **session_kwargs):
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        try:
            self.sock.bind(address)
            self.sock.listen(request_queue_size)
        except:  # noqa
            self.sock.close()
            raise
        logging.info(f"server listening at {self.sock.getsockname()}")
        self._is_shutdown = False
        self._shutdown_event = threading.Event()
        if not issubclass(session_type, Session):
            raise TypeError(f"Expect subclass of Session, but got {session_type}.")
        self.session_type = session_type
        self.session_params = (session_args, session_kwargs)

    def shutdown(self):
        self._is_shutdown = True
        self._shutdown_event.wait()

    def serve(self, poll_interval):
        self._shutdown_event.clear()
        try:
            with _ServerSelector() as selector:
                selector.register(self.sock, selectors.EVENT_READ)

                while not self._is_shutdown:
                    ready = selector.select(poll_interval)
                    if ready:
                        self._handle_request_noblock()
        finally:
            self._is_shutdown = False
            self._shutdown_event.set()
            logging.info("server exit")

    def _handle_request_noblock(self):
        try:
            request, client_address = self.sock.accept()
        except OSError:
            return
        logging.debug(f"connected from {client_address}")
        if self.verify_request(request, client_address):
            try:
                self.process_request(request, client_address)
            except Exception as error:
                logging.error("server handle error")
                handle_error(error, client_address)
                shutdown_request(request)
            except:  # noqa
                shutdown_request(request)
                raise
        else:
            shutdown_request(request)

    def verify_request(self, request, client_address):
        return True

    def process_request(self, request, client_address):
        session_args, session_kwargs = self.session_params
        session = self.session_type(*session_args, **session_kwargs)
        session.session_id = str(uuid.uuid4())
        threading.Thread(
            target=session.start,
            args=(request, client_address),
            daemon=True
        ).start()
