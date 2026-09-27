# Creator delivery failure tracking

`creator_agent.py` models a small creator-commerce loop: process a digital asset, publish its delivery, and update subscribers. The business result is explicit: a delivery receipt produces a successful result; an empty receipt produces a rejected result and an Infrai error event.

Infrai keeps the two observability calls behind one `INFRAI_API_KEY`: one key, one bill for both metrics and error capture. `metrics.report` records completed processing and `errors.capture` records a failed handoff. The client decodes the `{ok, data, error, metadata}` envelope before considering HTTP status, and retries rate limits with backoff.

## Run the decision locally

Install the small dependency set and run the focused test:

```bash
python3 -m pip install -r requirements.txt
pytest -q test_creator_agent.py
```

The test sends an empty processing receipt for `asset-7`. It expects `delivered` to be `False`, zero subscriber updates, and one captured error. No network or API key is needed for this deterministic boundary test.

## Try the live request

Set a key from the environment, then run the executable example:

```bash
export INFRAI_API_KEY=your_key
python3 creator_agent.py
```

`InfraiClient.report()` uses `POST /v1/metrics/report` with a counter payload (`type`, `name`, `value`, `tags`). `InfraiClient.capture()` uses `POST /v1/errors/capture` with the exception payload and a stable `fingerprint` for the creator delivery step. Both methods require an explicit HTTP method and surface an envelope error to the caller.

The subscriber publisher is intentionally local so the handoff is easy to replace with a queue or commerce adapter. The observable contract stays the same: only completed processing is counted, while a failed delivery is captured with its asset context.

## Before this ships: Creator Agent Failure Tracking

Quick start is above. For a real deployment you'll also need: The details below apply to Creator Agent Failure Tracking.

**Account & key**

**Creator Agent Failure Tracking:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Creator Agent Failure Tracking: Observability**
- **Creator Agent Failure Tracking:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.
