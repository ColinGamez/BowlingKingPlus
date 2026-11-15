import argparse
from http.server import ThreadingHTTPServer

from server.http import Handler


def main():
    parser = argparse.ArgumentParser(description="BowlingKingPlus development HTTP server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    with ThreadingHTTPServer((args.host, args.port), Handler) as service:
        print(f"BowlingKingPlus listening on http://{args.host}:{service.server_port}", flush=True)
        try:
            service.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
