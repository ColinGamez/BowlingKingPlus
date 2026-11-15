import argparse
from server.app import DevelopmentServer


def main():
    parser = argparse.ArgumentParser(description="BowlingKingPlus development HTTP server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--login-url", help="Login API base URL reachable by the test device")
    args = parser.parse_args()
    try:
        service = DevelopmentServer((args.host, args.port), login_url=args.login_url)
    except ValueError as error:
        parser.error(str(error))
    with service:
        print(f"BowlingKingPlus listening on http://{args.host}:{service.server_port}", flush=True)
        print(f"Bootstrap login URL: {service.bootstrap.login_url}", flush=True)
        try:
            service.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
