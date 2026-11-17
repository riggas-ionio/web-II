# Assignment 2026-27: Corfu Events & Bookings API

> 🇬🇷 [Ελληνική έκδοση](README.md)

Supporting files for the assignment. The assignment description itself is given separately (opencourses).

| File | What it is |
|---|---|
| [`openapi.yaml`](openapi.yaml) | The API specification (OpenAPI 3.1). **Binding**: the automated tests of the evaluation are based on it. |
| [`events.example.json`](events.example.json) | The format of your dataset (`data/events.json`): an array of `EventInput`. The events are **examples**, not real ones. |
| [`ionio-pay/`](ionio-pay/) | The course's (fake) payment provider. You run it as one more service in your `compose.yaml`. |

---

## `ionio-pay`

A small payment provider, in the spirit of Stripe, **with no real money**. Your API calls it to pay for a booking. It keeps its data in memory: a restart clears it.

### In your `compose.yaml`

Copy the `ionio-pay/` folder into your repo (unchanged):

```yaml
services:
  api:
    build: .
    environment:
      PAYMENT_URL: http://payments:8000
      PAY_SECRET_KEY: sk_test_ptd
      # ...
    depends_on:
      payments:
        condition: service_healthy

  payments:
    build: ./ionio-pay
    environment:
      PAY_SECRET_KEY: sk_test_ptd
      # WEBHOOK_URL: http://api:8000/api/v1/webhooks/ionio-pay   # bonus
    # No ports: the API finds it inside the Compose network.
    # For tests from your computer: ports: ["127.0.0.1:8090:8000"]
```

### Endpoints

All of them (except `/health`) need `Authorization: Bearer <PAY_SECRET_KEY>`.

| Method | Path | What it does |
|---|---|---|
| `POST` | `/v1/charges` | A charge. The `Idempotency-Key` header is **required**. Body: `{"amount_cents": 2400, "currency": "EUR", "card_token": "tok_visa", "reference": "booking-17"}` |
| `GET` | `/v1/charges/{id}` | One charge |
| `GET` | `/v1/charges?reference=booking-17` | The charges of a booking (useful after a timeout) |
| `POST` | `/v1/refunds` | A refund (bonus). `Idempotency-Key` header. Body: `{"charge_id": "ch_..."}` |
| `GET` | `/health` | For `depends_on` / `HEALTHCHECK` |

A successful charge: `201` with the charge (`"status": "succeeded"`). Errors have a **different shape** from your own API, `{"error": {"type": ..., "code": ..., "message": ...}}`; your API translates them into its own `Error`.

### Test tokens

| `card_token` | Result |
|---|---|
| `tok_visa` | `201`, success |
| `tok_declined` | `402`, `code` = `card_declined` |
| `tok_insufficient_funds` | `402`, `code` = `insufficient_funds` |
| `tok_slow` | Success, but the response takes `SLOW_SECONDS` (default 10). The charge **has already been made** when your API times out. |
| `tok_error` | `500` |
| `tok_flaky` | `503` the first time for each `Idempotency-Key`, success when retried with the **same** key |

### Idempotency

Same `Idempotency-Key` with the same body: the **same** response is returned, with no new charge, and with the header `Idempotent-Replayed: true`. Same key with a different body: `409` `idempotency_key_reused`. That is why, after a timeout or a `503`, your API retries with the **same** key.

### Configuration (environment)

| Variable | Default | |
|---|---|---|
| `PAY_SECRET_KEY` | `sk_test_ptd` | The key it expects in `Authorization` |
| `SLOW_SECONDS` | `10` | Delay of `tok_slow` |
| `LATENCY_MS` | `0` | Delay on **every** request |
| `FAILURE_RATE` | `0` | Probability (0-1) of a random `503`, before any charge |
| `WEBHOOK_URL` | (none) | Bonus: where it sends `charge.succeeded` / `charge.refunded` |
| `WEBHOOK_SECRET` | `whsec_test_ptd` | For signing the webhooks |

### Webhooks (bonus)

A `POST` to `WEBHOOK_URL` with body `{"id": "evt_...", "type": "charge.succeeded", "created_at": ..., "data": {charge}}` and the header:

```
Ionio-Pay-Signature: t=<unix time>,v1=<hex HMAC-SHA256 of "<t>.<raw body>" with key WEBHOOK_SECRET>
```

Verify the signature with `hmac.compare_digest` before you trust the content. Delivery is attempted **once**: your API must not rely on webhooks alone.

### Quick test

```bash
docker build -t ionio-pay ./ionio-pay
docker run --rm -p 127.0.0.1:8090:8000 ionio-pay
```
```bash
curl -i -X POST http://127.0.0.1:8090/v1/charges \
     -H "Authorization: Bearer sk_test_ptd" \
     -H "Idempotency-Key: test-1" \
     -H "Content-Type: application/json" \
     -d '{"amount_cents": 1200, "currency": "EUR", "card_token": "tok_visa", "reference": "booking-1"}'
```

---

## Checking your implementation against the spec

As in Exercise 5 of Lab 7, with your stack running and a user's API key:

```bash
schemathesis run _assignment/openapi.yaml --url http://127.0.0.1:8000/api/v1 \
    -H "X-API-Key: <key>" --checks all
```

**Never** on a database whose data you care about: it writes many random records. Give the test user a high `rate_limit`, otherwise most responses will be `429`.
