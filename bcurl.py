"""bcurl: BHTTP v1 client.   Usage: bcurl [-v] host[:port]/path

Exit codes: 0 success, 22 for a 4xx/5xx response, 1 for network/protocol errors.
Opens exactly one connection.
"""
import socket
import sys

from proto import (ConnectionClosed, F_END_STREAM, ProtocolError, T_DATA,
                   T_RESPONSE, decode_response, describe, encode_request,
                   hexdump, read_frame)

DEFAULT_PORT = 9000
REQ_ID = 1


def parse_target(target):
    if target.startswith("http://"):
        target = target[len("http://"):]
    hostport, slash, rest = target.partition("/")
    path = "/" + rest
    host, colon, port = hostport.partition(":")
    if not host or (colon and not port.isdigit()):
        raise ValueError(f"bad target: {target!r}")
    return host, int(port) if colon else DEFAULT_PORT, path


def fetch(host, port, path, out, verbose=False, err=sys.stderr):
    """One connection, one request. Writes body to out. Returns HTTP status."""
    def show(direction, label, raw):
        if verbose:
            print(f"{direction} {label}", file=err)
            print(hexdump(raw, prefix=f"{direction} "), file=err)

    with socket.create_connection((host, port)) as sock:
        headers = [("host", f"{host}:{port}"), ("user-agent", "bcurl/1"), ("accept", "*/*")]
        request = encode_request(REQ_ID, path, headers)
        show(">", f"REQUEST id={REQ_ID} len={len(request) - 8}", request)
        sock.sendall(request)

        status = None
        while True:
            frame = read_frame(sock)
            if frame is None:
                raise ConnectionClosed("server closed before end of response")
            show("<", describe(frame), frame.raw)
            if frame.req_id != REQ_ID and frame.type in (T_RESPONSE, T_DATA):
                raise ProtocolError(f"unexpected request id {frame.req_id}")
            if frame.type == T_RESPONSE and status is None:
                status, _ = decode_response(frame.payload)
            elif frame.type == T_DATA and status is not None:
                out.write(frame.payload)
                if frame.flags & F_END_STREAM:
                    return status
            # anything else is an unknown frame type: skip it cleanly


def main(argv):
    args = argv[1:]
    verbose = "-v" in args
    args = [a for a in args if a != "-v"]
    if len(args) != 1:
        print("usage: bcurl [-v] host[:port]/path", file=sys.stderr)
        return 2
    try:
        host, port, path = parse_target(args[0])
        status = fetch(host, port, path, sys.stdout.buffer, verbose)
        sys.stdout.buffer.flush()
    except (ValueError, OSError, ProtocolError, ConnectionClosed) as e:
        print(f"bcurl: {e}", file=sys.stderr)
        return 1
    return 22 if status >= 400 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
