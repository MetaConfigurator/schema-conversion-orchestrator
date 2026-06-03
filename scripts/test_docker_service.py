#!/usr/bin/env python3
"""
Black-box integration test for a *running* schema-converter container.

Unlike tests/ (which inject mock converters into the Flask app in-process),
this script talks to the real HTTP service over the network — exactly how
MetaConfigurator's backend will reach it. It exercises the real, registered
Python/Java/Node/Robot converters inside the image.

Usage:
    # against the local docker-compose service (default)
    python3 test_docker_service.py

    # against any other base URL (e.g. behind the nginx proxy)
    BASE_URL=http://localhost:5002 python3 test_docker_service.py
    BASE_URL=https://example.org/schema-converter python3 test_docker_service.py

Exit code is 0 if every check passes, 1 otherwise. No third-party deps.
"""

import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5002").rstrip("/")
TIMEOUT = float(os.environ.get("TIMEOUT", "120"))

# ANSI colors (disabled when not a TTY)
_C = sys.stdout.isatty()
GREEN = "\033[32m" if _C else ""
RED = "\033[31m" if _C else ""
DIM = "\033[2m" if _C else ""
RESET = "\033[0m" if _C else ""

_passed = 0
_failed = 0


def _request(method, path, body=None):
    """Return (status_code, parsed_json_or_text)."""
    url = f"{BASE_URL}{path}"
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode()
            status = resp.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        status = e.code
    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, raw


def check(name, condition, detail=""):
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"  {GREEN}✓{RESET} {name}")
    else:
        _failed += 1
        print(f"  {RED}✗ {name}{RESET}")
        if detail:
            print(f"    {DIM}{detail}{RESET}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_health():
    print("health:")
    status, data = _request("GET", "/health")
    check("GET /health -> 200", status == 200, f"got {status}")
    check("status == ok", isinstance(data, dict) and data.get("status") == "ok", f"got {data}")


def test_convert_jsonschema_to_linkml():
    print("convert JsonSchema -> LinkMl (direct path):")
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Person",
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
    }
    status, data = _request("POST", "/convert", {
        "sourceLanguage": "JsonSchema",
        "targetLanguage": "LinkMl",
        "schema": schema,
    })
    check("POST /convert -> 200", status == 200, f"got {status}: {data}")
    results = data.get("results") if isinstance(data, dict) else None
    check("response has non-empty 'results'", bool(results), f"got {data}")
    if not results:
        return

    first = results[0]
    check("result item has success/result/conversionPath fields",
          all(k in first for k in ("success", "result", "conversionPath")),
          f"got keys {list(first.keys())}")

    any_success = any(r.get("success") for r in results)
    # The CI only asserts results exist; a real converter *should* succeed.
    # Report it but treat a successful conversion as the meaningful check.
    check("at least one conversion path succeeded", any_success,
          "no path returned success=True — converter ran but produced no valid output")
    if any_success:
        best = next(r for r in results if r.get("success"))
        preview = str(best.get("result"))[:200].replace("\n", " ")
        print(f"    {DIM}best result preview: {preview}{RESET}")


def test_unknown_language_400():
    print("convert with unknown language:")
    status, data = _request("POST", "/convert", {
        "sourceLanguage": "FakeLang",
        "targetLanguage": "LinkMl",
        "schema": "{}",
    })
    check("unknown source language -> 400", status == 400, f"got {status}: {data}")
    check("response contains 'error'", isinstance(data, dict) and "error" in data, f"got {data}")


def test_no_path_400():
    print("convert with no available path:")
    status, data = _request("POST", "/convert", {
        "sourceLanguage": "Mermaid",
        "targetLanguage": "Protobuf",
        "schema": "{}",
    })
    check("no conversion path -> 400", status == 400, f"got {status}: {data}")


def main():
    print(f"Testing schema-converter at {BASE_URL}\n")
    test_health()
    test_convert_jsonschema_to_linkml()
    test_unknown_language_400()
    test_no_path_400()

    print()
    total = _passed + _failed
    if _failed:
        print(f"{RED}{_failed}/{total} checks FAILED{RESET}")
        sys.exit(1)
    print(f"{GREEN}all {total} checks passed{RESET}")


if __name__ == "__main__":
    main()
