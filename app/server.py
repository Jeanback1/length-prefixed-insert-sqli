"""Local lab: a length-prefixed record is checked, then concatenated into INSERT.

LAB_MODE=vulnerable returns the database error text.
LAB_MODE=safe binds the body as a parameter and returns a generic error.
"""

import os

import psycopg
from flask import Flask, jsonify, request

app = Flask(__name__)

PREFIX = "v1|"
LENGTH_DIGITS = 4
MAX_BODY = 180
MODE = os.environ.get("LAB_MODE", "vulnerable")
DSN = os.environ.get(
    "DATABASE_URL",
    "postgresql://app:app@db:5432/lab",
)


def parse_record(raw):
    """Return the body only when the declared byte length matches."""
    if not isinstance(raw, str) or not raw.startswith(PREFIX):
        raise ValueError("BAD_PREFIX")
    rest = raw[len(PREFIX):]
    if len(rest) < LENGTH_DIGITS + 1 or rest[LENGTH_DIGITS] != "|":
        raise ValueError("BAD_LENGTH")
    declared_text = rest[:LENGTH_DIGITS]
    try:
        declared = int(declared_text, 16)
    except ValueError as exc:
        raise ValueError("BAD_LENGTH") from exc
    body = rest[LENGTH_DIGITS + 1:]
    size = len(body.encode())
    if declared != size or declared > MAX_BODY:
        raise ValueError("LENGTH_MISMATCH")
    return body


def store(body, safe):
    with psycopg.connect(DSN) as conn:
        with conn.cursor() as cur:
            if safe:
                cur.execute("INSERT INTO notes (body) VALUES (%s)", (body,))
            else:
                statement = "INSERT INTO notes (body) VALUES ('" + body + "')"
                cur.execute(statement)


@app.get("/health")
def health():
    return jsonify(ok=True, mode=MODE)


@app.post("/notes")
def notes():
    payload = request.get_json(silent=True) or {}
    try:
        body = parse_record(payload.get("record", ""))
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    safe = MODE == "safe"
    try:
        store(body, safe)
    except psycopg.Error as exc:
        if safe:
            return jsonify(error="STORE_FAILED"), 500
        detail = "database error"
        if exc.diag is not None and exc.diag.message_primary:
            detail = exc.diag.message_primary
        return jsonify(error="QUERY_FAILED", detail=detail), 500
    return jsonify(stored=True), 201
