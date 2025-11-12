#!/usr/bin/env python3
"""Example Anthropic client (Python).

This example shows a minimal pattern for selecting the model from the
`ANTHROPIC_DEFAULT_MODEL` environment variable and how to make a simple
HTTP request to Anthropic's completions endpoint using `requests`.

Behavior:
- If `ANTHROPIC_API_KEY` is not set, the script will only print the selected model.
- If `ANTHROPIC_API_KEY` is set and `RUN_LIVE_SMOKE_TEST` is truthy (1/true), the script
  will perform a single minimal request and print a short result.

Note: For production code prefer the official Anthropic SDK (if available),
handle retries, timeouts, rate limits, and do not print secrets or large responses.
"""
from __future__ import annotations

import os
import sys
import json


def get_default_model() -> str:
    return os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-4.5-haiku")


def print_status(model: str, api_key: str | None) -> None:
    print("Using model:", model)
    print("ANTHROPIC_API_KEY:", "set" if api_key else "<not set>")


def live_call(api_key: str, model: str) -> int:
    """Make a minimal request using requests. Returns 0 on success, non-zero on failure."""
    try:
        import requests
    except Exception:
        print("The 'requests' library is not installed. Install requirements to run live calls.")
        return 3

    url = "https://api.anthropic.com/v1/complete"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": "Human: Give me a one-line friendly greeting.\nAssistant:",
        "max_tokens_to_sample": 40,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print("HTTP status:", resp.status_code)
        try:
            j = resp.json()
            print("Response (truncated):")
            s = json.dumps(j, indent=2)
            print(s[:1000])
        except Exception:
            print("Non-JSON response:")
            print(resp.text[:1000])
        return 0 if resp.status_code // 100 == 2 else 4
    except Exception as e:
        print("Live request failed:", str(e), file=sys.stderr)
        return 5


def main() -> int:
    model = get_default_model()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    run_live = os.getenv("RUN_LIVE_SMOKE_TEST", "0").lower() in ("1", "true", "yes")

    print_status(model, api_key)

    if run_live:
        if not api_key:
            print("RUN_LIVE_SMOKE_TEST is set but ANTHROPIC_API_KEY is not provided.")
            return 2
        return live_call(api_key, model)

    print("Not running live request. To enable, set ANTHROPIC_API_KEY and RUN_LIVE_SMOKE_TEST=1")
    return 0


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)
