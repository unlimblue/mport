import urllib.parse


def parse_hostport(hp):
    # urlparse() and urlsplit() insists on absolute URLs starting with "//"
    result = urllib.parse.urlsplit('//' + hp)
    return result.hostname, result.port


if __name__ == "__main__":
    import logging
    import argparse
    from mport import __version__
    from mport.server import Server
    from mport.pm_session import PortMappingSession

    parser = argparse.ArgumentParser(
        f"Port mapping [v{__version__}]",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-l', "--listen", type=str, default="localhost:11022", help="Server listening address")
    parser.add_argument('-t', "--target", required=True, type=str, help="Target address")
    parser.add_argument("--timeout", type=float, default=None, help="Port mapping timeout [second]")
    parser.add_argument("--debug", action="store_true", default=False, help="Set logger level to debug")

    args = parser.parse_args()

    logging.basicConfig(
        format='%(asctime)s  %(levelname)-10s %(processName)s  %(name)s \033[0;33m%(message)s\033[0m',
        datefmt="%Y-%m-%d-%H-%M-%S",
        level=logging.DEBUG if args.debug else logging.INFO
    )

    server = Server(
        parse_hostport(args.listen),
        5,
        PortMappingSession,
        parse_hostport(args.target),
        timeout=args.timeout
    )

    server.serve(0.5)
