import hashlib
import json
from uuid import uuid4


def create_id(prefix: str) -> str:
    """Return a short opaque ID with the given prefix (for example ``wr_``)."""
    return f"{prefix}{uuid4().hex[:12]}"


def compute_payload_hash(payload: dict) -> str:
    """SHA-256 of canonical JSON for idempotent body comparison.

    Uses stable key order and minimal separators so equivalent payloads
    produce the same hash regardless of whitespace in the original request.
    """
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
