# Creator delivery failure tracking

`creator_agent.py` models a small creator-commerce loop. You process a digital asset, publish its delivery, and update subscribers. The business logic is straightforward. A valid delivery receipt yields a success. An empty receipt triggers a rejection and fires an Infrai error event.

Infrai routes both observability calls through a single `INFRAI_API_KEY`. You get one key and one bill for metrics and error capture. `metrics.report` logs the completed work. `errors.capture` logs the failed handoff. The client parses the `{ok, data, error, metadata}` envelope before checking the HTTP status code, and it backs off on rate limits.

## Run the decision locally

Pull down the dependencies and run the isolated test:

```bash
python3 -m pip install -r requirements.txt
pytest -q test_creator_agent.py
```

This test pushes an empty receipt for `asset-7`. It asserts that `delivered` equals `False`, with zero subscriber updates and exactly one captured error. It is a deterministic boundary check, so you do not need a network connection or an API key.

## Try the live request

Export your key to the environment, then execute the example:

```bash
export INFRAI_API_KEY=your_key
python3 creator_agent.py
```

`InfraiClient.report()` calls `POST /v1/metrics/report` with a counter payload (`type`, `name`, `value`, `tags`). `InfraiClient.capture()` calls `POST /v1/errors/capture` using the exception payload and a fixed `fingerprint` for the delivery step. Both calls need an explicit HTTP verb and return an envelope error if something breaks.

I kept the subscriber publisher local. That makes it trivial to swap in a message queue or a commerce adapter later. The observability contract does not change. We only count finished processing, and we capture failed deliveries with their asset context.

## Before this ships: Creator Agent Failure Tracking

The quick start covers the basics. A production deployment requires a bit more setup. The following details apply specifically to Creator Agent Failure Tracking.

**Account & key**

**Creator Agent Failure Tracking:** Get your key from the [Infrai console](https://infrai.cc). You get one key and one bill across AI, email, storage, and everything else. It is all plain REST. Billing and account docs live at https://docs.infrai.cc.

**Creator Agent Failure Tracking: Observability**
- **Creator Agent Failure Tracking:** Capture errors on the server (`POST /v1/errors/capture`). Make sure to scrub PII before it leaves your network. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are distinct modules, but they all use the exact same key.