#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from urllib.request import urlopen


def fetch_json(url: str) -> dict:
    with urlopen(url, timeout=20) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check API health and agents routes.")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="API base URL (default: http://127.0.0.1:8000)",
    )
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    health = fetch_json(f"{base}/health")
    agents = fetch_json(f"{base}/agents")

    print("health:", json.dumps(health, indent=2))
    print("agents:", json.dumps(agents, indent=2))


if __name__ == "__main__":
    main()

