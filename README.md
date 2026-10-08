# BHTTP Client

This project is a Python client (`bcurl`) for BHTTP, a simple binary HTTP-like protocol over TCP. Instead of plain text HTTP, BHTTP sends requests and responses inside binary frames with fixed 8-byte headers.

This repository contains both sides of the protocol so that the project can be tested locally. For the assignment, I am submitting the client implementation (`bcurl`).

## What it does

The `bcurl` client:

- Opens a TCP connection to the specified host and port (default port `9000`).
- Builds and sends a binary `REQUEST` frame over the socket.
- Receives `RESPONSE` and `DATA` frames from the server.
- Writes the response body directly to stdout.
- Supports a `-v` flag to print hex dumps of sent and received frames to stderr.
- Exits with `0` for success (2xx/3xx), `22` for HTTP error status (4xx/5xx), and `1` for network or protocol errors.

## Running it

First, start the test server in one terminal:

```bash
mkdir -p www
echo '<html><body><h1>Hello from BHTTP!</h1></body></html>' > www/index.html
./bserve ./www 9000
```

Then, run the client from another terminal:

```bash
./bcurl localhost:9000/index.html
```

Output:

```html
<html>
  <body>
    <h1>Hello from BHTTP!</h1>
  </body>
</html>
```

For verbose frame dumps:

```bash
./bcurl -v localhost:9000/index.html
```

Output:

```text
> REQUEST id=1 len=48
> 00000000  00 00 30 01 00 00 00 01 01 00 0b 2f 69 6e 64 65  |..0......../inde|
> 00000010  78 2e 68 74 6d 6c 03 81 00 0e 6c 6f 63 61 6c 68  |x.html....localh|
> 00000020  6f 73 74 3a 39 30 30 30 82 00 07 62 63 75 72 6c  |ost:9000...bcurl|
> 00000030  2f 31 83 00 03 2a 2f 2a                          |/1...*/*|
< RESPONSE id=1 flags=0x00 len=31
< 00000000  00 00 1f 02 00 00 00 01 00 c8 03 86 00 08 62 73  |..............bs|
< 00000010  65 72 76 65 2f 31 85 00 09 74 65 78 74 2f 68 74  |erve/1...text/ht|
< 00000020  6d 6c 84 00 02 35 33                             |ml...53|
< DATA id=1 flags=0x01 len=53
< 00000000  00 00 35 03 01 00 00 01 3c 68 74 6d 6c 3e 3c 62  |..5.....<html><b|
< 00000010  6f 64 79 3e 3c 68 31 3e 48 65 6c 6c 6f 20 66 72  |ody><h1>Hello fr|
< 00000020  6f 6d 20 42 48 54 54 50 21 3c 2f 68 31 3e 3c 2f  |om BHTTP!</h1></|
< 00000030  62 6f 64 79 3e 3c 2f 68 74 6d 6c 3e 0a           |body></html>.|
<html><body><h1>Hello from BHTTP!</h1></body></html>
```

## Project files

- `bcurl` — Shell launcher script for the client
- `bcurl.py` — Client implementation
- `proto.py` — Framing, header encoding/decoding, and protocol helpers
- `test_bhttp.py` — Unit test suite
- `SPEC.md` — Protocol specification
- `hexdump.md` — Annotated example of an actual request and response exchange
- `bserve` / `bserve.py` — Local test server

## Testing

Run the test suite with:

```bash
python3 -m unittest -v
```

Output:

```text
test_200 (test_bhttp.BHTTPTest.test_200) ... ok
test_404 (test_bhttp.BHTTPTest.test_404) ... ok
test_bad_method_400 (test_bhttp.BHTTPTest.test_bad_method_400) ... ok
test_bcurl_cli_exit_codes_and_verbose (test_bhttp.BHTTPTest.test_bcurl_cli_exit_codes_and_verbose) ... ok
test_bcurl_function_single_connection (test_bhttp.BHTTPTest.test_bcurl_function_single_connection) ... ok
test_keep_alive_multiple_requests (test_bhttp.BHTTPTest.test_keep_alive_multiple_requests) ... ok
test_large_file_multi_frame (test_bhttp.BHTTPTest.test_large_file_multi_frame) ... ok
test_malformed_payload_400_and_stays_open (test_bhttp.BHTTPTest.test_malformed_payload_400_and_stays_open) ... ok
test_oversize_frame_400_then_close (test_bhttp.BHTTPTest.test_oversize_frame_400_then_close) ... ok
test_root_and_dir_index (test_bhttp.BHTTPTest.test_root_and_dir_index) ... ok
test_traversal_is_404 (test_bhttp.BHTTPTest.test_traversal_is_404) ... ok
test_unknown_frame_type_skipped (test_bhttp.BHTTPTest.test_unknown_frame_type_skipped) ... ok
test_unknown_header_literal_roundtrip (test_bhttp.BHTTPTest.test_unknown_header_literal_roundtrip) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.095s

OK
```

## Protocol

For the complete protocol specification, including frame header formats, static header table indices, and error handling rules, see [SPEC.md](SPEC.md).
