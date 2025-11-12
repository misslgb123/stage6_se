## Enable Claude Haiku 4.5 for all clients (repo-level toggle)

This repository now includes a repo-level default for Anthropic model selection.

- `ANTHROPIC_DEFAULT_MODEL` is exported in `setup.sh` for local development.
- `ANTHROPIC_DEFAULT_MODEL` is also set as an `ENV` in the `Dockerfile` for container builds.

Default value: `claude-4.5-haiku` (can be overridden by setting the environment variable in the runtime environment).

How it works

1. Local dev: run `source setup.sh` (or run the steps in it). That script exports `ANTHROPIC_DEFAULT_MODEL` if not already set in your environment.
2. Containers: the Dockerfile sets the `ANTHROPIC_DEFAULT_MODEL` environment variable at build/runtime.
3. Client applications should read `ANTHROPIC_DEFAULT_MODEL` and use it when selecting a model for requests.

Recommended application change (Python example):

```python
import os

DEFAULT_MODEL = os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-4.5-haiku")
# Use DEFAULT_MODEL when creating requests to the Anthropic SDK / API
```

Verification

- Run the smoke test `scripts/smoke_test_anthropic.py` to confirm the environment provides the expected model name.

Rollback

- Remove or change the `ANTHROPIC_DEFAULT_MODEL` entries from `setup.sh` and `Dockerfile` and redeploy.

Notes

- This change only affects code that is updated to read the `ANTHROPIC_DEFAULT_MODEL` variable. If some clients hard-code a model, update them separately.
- Do NOT store your Anthropic API key in the repo; use environment variables or your secret manager for the key.

# Enabling Claude Haiku 4.5 (repo-level toggle)

This file documents the small, reversible repository changes made to provide a repo-level default for the Anthropic model "claude-4.5-haiku".

What changed

- `setup.sh`: export `ANTHROPIC_DEFAULT_MODEL="claude-4.5-haiku"` for local development.
- `Dockerfile`: added `ENV ANTHROPIC_DEFAULT_MODEL=claude-4.5-haiku` so containers inherit the default.

Why this approach

- Simple and reversible. Code that reads this environment variable can adopt the new default without changing every call site.

How to use

1. For local development, run `source setup.sh` (or set the variable manually) and ensure `ANTHROPIC_API_KEY` is present when calling the Anthropic API.
2. For containers, the `ENV` is baked in by the Dockerfile. Override at runtime with `-e ANTHROPIC_DEFAULT_MODEL=...` if needed.

Rollout and rollback

- Rollout: merge this change and deploy. Update your client SDKs to prefer `process.env.ANTHROPIC_DEFAULT_MODEL` (Node) or `os.getenv("ANTHROPIC_DEFAULT_MODEL")` (Python).
- Rollback: revert the commit or remove the `ENV` / `export` lines. Alternatively, set an explicit model override in your runtime/CI.

Safety notes

- Verify the exact model identifier with Anthropic or your provider console (this document assumes `claude-4.5-haiku`).
- Confirm billing and rate limits with your org's Anthropic account before rolling out to production.

Smoke test

- A tiny smoke-test script is included at `scripts/smoke_test_anthropic.py` which prints the selected model (and will attempt no network requests unless you add an SDK call).

Next steps

- Update application code to read the environment variable when selecting models.
- Optionally add a CI job that runs the smoke test and fails if the env var is missing.

CI integration

- This repository now includes an optional CI job in `.github/workflows/pr_tests.yml` named
  `pr_tests_live_smoke`. The job runs only when the repository `secrets.ANTHROPIC_API_KEY` is
  populated in GitHub Actions settings. When enabled the job will run `scripts/smoke_test_anthropic.py`
  inside the container with `RUN_LIVE_SMOKE_TEST=1` so the script performs a minimal live request.

Security note: keep `ANTHROPIC_API_KEY` in your repository/organization secrets (not in code). The
CI job will only run when the secret is present.
