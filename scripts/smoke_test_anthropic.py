#!/usr/bin/env python3
"""Lightweight smoke test: print selected Anthropic model and optionally run a live request.

Behavior:
- Always prints `ANTHROPIC_DEFAULT_MODEL` and whether `ANTHROPIC_API_KEY` is present.
- If `ANTHROPIC_API_KEY` is set and `RUN_LIVE_SMOKE_TEST` is truthy (1/true), the script
  will attempt a minimal POST to the Anthropic completions endpoint and print a short result.

The live request is optional to avoid requiring secrets in all environments (CI will opt-in).
This script uses the `requests` library (added to `requirements.txt`) so the Docker image
and local venv must have `requests` installed for the live test to run.
"""
import os
import sys
import json


def print_env_status(model: str | None, api_key: str | None) -> None:
    print("ANTHROPIC_DEFAULT_MODEL:", model or "<not set>")
    print("ANTHROPIC_API_KEY:", "set" if api_key else "<not set>")


def run_live_request(api_key: str, model: str) -> int:
    """Make a minimal POST to Anthropic's completions endpoint.

    Returns exit code 0 on success, non-zero on failure.
    """
    try:
        import requests
    except Exception as e:
        print("Live test skipped: 'requests' library is not installed.", file=sys.stderr)
        print("Install requests (added to requirements.txt) to enable live smoke tests.")
        return 3

    url = "https://api.anthropic.com/v1/complete"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "prompt": "Human: Say hello in one short sentence.\nAssistant:",
        "max_tokens_to_sample": 40,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        print("Live request status:", resp.status_code)
        try:
            j = resp.json()
            # Print a compact representation of the result (truncate for safety)
            s = json.dumps(j, indent=2)
            print("Response (truncated 1000 chars):")
            print(s[:1000])
        except Exception:
            print("Response content (non-json):")
            print(resp.text[:1000])
        return 0 if resp.status_code // 100 == 2 else 4
    except Exception as e:
        print("Live request failed:", str(e), file=sys.stderr)
        return 5


def main():
    model = os.getenv("ANTHROPIC_DEFAULT_MODEL")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    run_live = os.getenv("RUN_LIVE_SMOKE_TEST", "0").lower() in ("1", "true", "yes")

    print_env_status(model, api_key)

    if not model:
        print("Warning: no default model set. Set ANTHROPIC_DEFAULT_MODEL to enable tests.")
        # do not treat as fatal for CI that only checks presence of env var elsewhere
    if run_live:
        if not api_key:
            print("RUN_LIVE_SMOKE_TEST is set but ANTHROPIC_API_KEY is not provided.")
            return 2
        if not model:
            print("Cannot run live test because ANTHROPIC_DEFAULT_MODEL is not set.")
            return 2
        return run_live_request(api_key, model)

    # If not running live, exit success (0) so CI/pipelines can use this as a presence check
    return 0


if __name__ == "__main__":
    code = main()
    sys.exit(code)
