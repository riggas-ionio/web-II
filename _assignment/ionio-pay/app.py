"""ionio-pay: a fake payment provider for the 2026-27 assignment.

State lives in memory, so run it with a single worker (see the Dockerfile).
Restarting the container clears every charge.
"""
import hashlib
import hmac
import json
import os
import random
import secrets
import threading
import time
import urllib.request
from datetime import datetime, timezone

from flask import Flask, request

app = Flask(__name__)

SECRET_KEY = os.environ.get('PAY_SECRET_KEY', 'sk_test_ptd')
SLOW_SECONDS = float(os.environ.get('SLOW_SECONDS', 10))
LATENCY_MS = int(os.environ.get('LATENCY_MS', 0))
FAILURE_RATE = float(os.environ.get('FAILURE_RATE', 0))
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', 'whsec_test_ptd')

DECLINES = {'tok_declined': 'card_declined', 'tok_insufficient_funds': 'insufficient_funds'}
TOKENS = {'tok_visa', 'tok_slow', 'tok_error', 'tok_flaky', *DECLINES}

lock = threading.Lock()
charges = {}        # charge id -> charge
refunds = {}        # refund id -> refund
idempotency = {}    # (endpoint, key) -> (fingerprint, status, body)
flaky_failed = set()


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def error(status, code, message, type_='invalid_request_error'):
    return {'error': {'type': type_, 'code': code, 'message': message}}, status


def fingerprint(body):
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def send_webhook(event_type, data):
    if not WEBHOOK_URL:
        return
    body = json.dumps({'id': 'evt_' + secrets.token_hex(8), 'type': event_type,
                       'created_at': now(), 'data': data}).encode()
    ts = str(int(time.time()))
    sig = hmac.new(WEBHOOK_SECRET.encode(), f'{ts}.'.encode() + body, hashlib.sha256).hexdigest()
    req = urllib.request.Request(WEBHOOK_URL, data=body, method='POST', headers={
        'Content-Type': 'application/json',
        'Ionio-Pay-Signature': f't={ts},v1={sig}',
    })

    def deliver():
        try:
            urllib.request.urlopen(req, timeout=5).close()
        except Exception as e:      # one attempt only; the receiver must not rely on webhooks alone
            app.logger.warning('webhook %s failed: %s', event_type, e)

    threading.Thread(target=deliver, daemon=True).start()


@app.before_request
def auth_and_chaos():
    if not request.path.startswith('/v1/'):
        return
    if LATENCY_MS:
        time.sleep(LATENCY_MS / 1000)
    if not hmac.compare_digest(request.headers.get('Authorization', ''), f'Bearer {SECRET_KEY}'):
        return error(401, 'invalid_api_key', 'Use the header Authorization: Bearer <PAY_SECRET_KEY>',
                     'authentication_error')
    if FAILURE_RATE and random.random() < FAILURE_RATE:
        return error(503, 'service_unavailable', 'Random failure (FAILURE_RATE)', 'api_error')


def read_body(fields):
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return None, error(400, 'invalid_body', 'The body must be a JSON object')
    for name, check in fields.items():
        if not check(body.get(name)):
            return None, error(400, 'invalid_' + name, f'Invalid or missing {name}')
    return body, None


def replay_or_none(endpoint, key, fp):
    """Returns the stored response for this key, an error, or None for a new key."""
    stored = idempotency.get((endpoint, key))
    if stored is None:
        return None
    if stored[0] != fp:
        return error(409, 'idempotency_key_reused',
                     'This Idempotency-Key was used with different parameters')
    return stored[2], stored[1], {'Idempotent-Replayed': 'true'}


@app.post('/v1/charges')
def create_charge():
    key = request.headers.get('Idempotency-Key')
    if not key:
        return error(400, 'missing_idempotency_key', 'The Idempotency-Key header is required')
    body, err = read_body({
        'amount_cents': lambda v: type(v) is int and v > 0,
        'currency': lambda v: v == 'EUR',
        'card_token': lambda v: isinstance(v, str),
        'reference': lambda v: isinstance(v, str) and 0 < len(v) <= 100,
    })
    if err:
        return err
    token = body['card_token']
    if token not in TOKENS:
        return error(400, 'invalid_card_token', f'Unknown test token; use one of {sorted(TOKENS)}')

    with lock:
        replay = replay_or_none('charges', key, fingerprint(body))
        if replay:
            return replay
        if token == 'tok_error':
            return error(500, 'internal_error', 'Simulated provider error', 'api_error')
        if token == 'tok_flaky' and key not in flaky_failed:
            flaky_failed.add(key)
            return error(503, 'service_unavailable', 'Simulated failure; retry with the same key', 'api_error')

        charge = {
            'id': 'ch_' + secrets.token_hex(8),
            'status': 'failed' if token in DECLINES else 'succeeded',
            'amount_cents': body['amount_cents'],
            'currency': 'EUR',
            'reference': body['reference'],
            'failure_code': DECLINES.get(token),
            'refunded': False,
            'created_at': now(),
        }
        charges[charge['id']] = charge
        if token in DECLINES:
            response, status = error(402, DECLINES[token], 'The card was declined', 'card_error')
            response['error']['charge_id'] = charge['id']
        else:
            status, response = 201, charge
        idempotency[('charges', key)] = (fingerprint(body), status, response)

    if token == 'tok_slow':
        time.sleep(SLOW_SECONDS)        # the charge already exists: a client timeout does not cancel it
    if status == 201:
        send_webhook('charge.succeeded', charge)
    return response, status


@app.get('/v1/charges/<charge_id>')
def get_charge(charge_id):
    charge = charges.get(charge_id)
    if charge is None:
        return error(404, 'resource_missing', f'No charge {charge_id}')
    return charge


@app.get('/v1/charges')
def list_charges():
    reference = request.args.get('reference')
    data = [c for c in charges.values() if reference is None or c['reference'] == reference]
    return {'data': data}


@app.post('/v1/refunds')
def create_refund():
    key = request.headers.get('Idempotency-Key')
    if not key:
        return error(400, 'missing_idempotency_key', 'The Idempotency-Key header is required')
    body, err = read_body({'charge_id': lambda v: isinstance(v, str)})
    if err:
        return err

    with lock:
        replay = replay_or_none('refunds', key, fingerprint(body))
        if replay:
            return replay
        charge = charges.get(body['charge_id'])
        if charge is None or charge['status'] != 'succeeded':
            return error(404, 'resource_missing', f"No successful charge {body['charge_id']}")
        if charge['refunded']:
            return error(409, 'charge_already_refunded', 'This charge was already refunded')
        charge['refunded'] = True
        refund = {
            'id': 're_' + secrets.token_hex(8),
            'charge_id': charge['id'],
            'amount_cents': charge['amount_cents'],
            'currency': 'EUR',
            'status': 'succeeded',
            'created_at': now(),
        }
        refunds[refund['id']] = refund
        idempotency[('refunds', key)] = (fingerprint(body), 201, refund)

    send_webhook('charge.refunded', charge)
    return refund, 201


@app.get('/health')
def health():
    return {'status': 'ok'}
