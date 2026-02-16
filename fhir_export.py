"""
DEPRECATED: FHIR Export Module

This module is for reference only and not actively used.
FHIR export functionality is integrated into the main Flask API.

Note: Uses legacy SQLite code - not updated for PostgreSQL migration.
"""

import sys
raise ImportError("This module is deprecated. FHIR functionality moved to Flask API.")

# === Legacy SQLite code below - DO NOT USE ===
import sqlite3
import json
import os
import hmac
import hashlib
from datetime import datetime, timezone
from cryptography.fernet import Fernet
from secrets_manager import SecretsManager
from typing import Tuple, List


# Determine debug mode locally
DEBUG = os.environ.get('DEBUG', '').lower() in ('1', 'true', 'yes')
secrets = SecretsManager(debug=DEBUG)

# Local decrypt helper using same ENCRYPTION_KEY sourcing as main
# SECURITY: Encryption key MUST be provided via environment variable or secrets manager.
# File-based key storage is NOT supported for security reasons.
_enc = secrets.get_secret("ENCRYPTION_KEY") or os.environ.get("ENCRYPTION_KEY")
if _enc:
    ENCRYPTION_KEY = _enc.encode() if isinstance(_enc, str) else _enc
    try:
        _cipher = Fernet(ENCRYPTION_KEY)
    except Exception as e:
        raise ValueError(f"Invalid ENCRYPTION_KEY format in fhir_export. Must be a valid Fernet key. Error: {e}")
else:
    # Do not raise at import time; allow the app to run without FHIR signing available.
    ENCRYPTION_KEY = None
    _cipher = None
    if DEBUG:
        # For local debug runs, generate a temporary key so signing can proceed if needed.
        import warnings
        warnings.warn(
            'ENCRYPTION_KEY not set in fhir_export; generating temporary key for DEBUG mode. '
            'FHIR signatures will NOT be verifiable after restart! '
            'Set ENCRYPTION_KEY env var for persistent signing.'
        )
        ENCRYPTION_KEY = Fernet.generate_key()
        _cipher = Fernet(ENCRYPTION_KEY)
    else:
        # In production, log the issue but don't crash at import
        print("WARNING: ENCRYPTION_KEY not set. FHIR export signing will fail in production.")

def _decrypt(v):
    if not v: return ""
    if _cipher is None:
        # If no cipher available, assume data is plaintext or already decrypted
        return v
    try:
        return _cipher.decrypt(v.encode()).decode()
    except Exception:
        return v


def _sign_bundle(bundle_json: str) -> str:
    # HMAC-SHA256 over bundle JSON using ENCRYPTION_KEY
    key = ENCRYPTION_KEY
    if not key:
        # Try to fetch at runtime from secrets manager or environment (tests may set env later)
        _enc = secrets.get_secret("ENCRYPTION_KEY") or os.environ.get("ENCRYPTION_KEY")
        if _enc:
            key = _enc.encode() if isinstance(_enc, str) else _enc
    if not key:
        raise RuntimeError('ENCRYPTION_KEY is required to sign FHIR bundles in production')
    sig = hmac.new(key, bundle_json.encode(), hashlib.sha256).hexdigest()
    signed = {
        "signedBundle": json.loads(bundle_json),
        "signature": {"algorithm": "hmac-sha256", "value": sig, "generatedAt": datetime.now(timezone.utc).isoformat()}
    }
    return json.dumps(signed, indent=2, default=str)


def validate_fhir_bundle(bundle_obj: dict) -> Tuple[bool, List[str]]:
    errors = []
    if not isinstance(bundle_obj, dict):
        return False, ["Bundle is not a JSON object"]
    if bundle_obj.get('resourceType') != 'Bundle':
        errors.append("resourceType must be 'Bundle'")
    if 'entry' not in bundle_obj or not isinstance(bundle_obj['entry'], list) or len(bundle_obj['entry']) == 0:
        errors.append('Bundle must have at least one entry')
    # Check for Patient resource
    patient_found = False
    for e in bundle_obj.get('entry', []):
        r = e.get('resource', {})
        if r.get('resourceType') == 'Patient':
            patient_found = True
            if not r.get('id'):
                errors.append('Patient.id is required')
            # name text or family/given advisable
            if not r.get('name') or not isinstance(r.get('name'), list) or len(r.get('name')) == 0:
                errors.append('Patient.name is required')
    if not patient_found:
        errors.append('No Patient resource found')

    # Basic check for Observations having effectiveDateTime
    for e in bundle_obj.get('entry', []):
        r = e.get('resource', {})
        if r.get('resourceType') == 'Observation':
            if not r.get('effectiveDateTime'):
                errors.append('Observation missing effectiveDateTime')

    return (len(errors) == 0), errors


def export_patient_fhir(username: str, signer: str = None, add_provenance: bool = True, sign_bundle: bool = True) -> str:
    conn = sqlite3.connect("therapist_app.db")
    cur = conn.cursor()

    # Patient profile
    p = cur.execute("SELECT full_name, dob, conditions FROM users WHERE username=%s", (username,)).fetchone()
    if p:
        full_name = _decrypt(p[0])
        dob = _decrypt(p[1])
        conditions = _decrypt(p[2])
    else:
        full_name = username
        dob = None
        conditions = None

    # Clinical scales
    scales = cur.execute("SELECT scale_name, score, severity, entry_timestamp FROM clinical_scales WHERE username=%s ORDER BY entry_timestamp DESC", (username,)).fetchall()

    # Mood logs - schema may vary between 'entry_timestamp' and 'entrestamp'
    try:
        moods = cur.execute("SELECT mood_val, sleep_val, meds, notes, entry_timestamp FROM mood_logs WHERE username=%s ORDER BY entry_timestamp DESC LIMIT 50", (username,)).fetchall()
        timestamp_col = 'entry_timestamp'
    except sqlite3.OperationalError:
        moods = cur.execute("SELECT mood_val, sleep_val, meds, notes, entrestamp FROM mood_logs WHERE username=%s ORDER BY entrestamp DESC LIMIT 50", (username,)).fetchall()
        timestamp_col = 'entrestamp'

    conn.close()

    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entry": []
    }

    patient = {
        "resource": {
            "resourceType": "Patient",
            "id": username,
            "name": [{"text": full_name}],
            "birthDate": dob if dob else None,
            "extension": [{"url": "http://example.org/fhir/StructureDefinition/conditions", "valueString": conditions}] if conditions else []
        }
    }
    bundle['entry'].append(patient)

    # Add clinical scales as Observations
    for s in scales:
        obs = {
            "resource": {
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": s[0]},
                "valueQuantity": {"value": s[1]},
                "interpretation": [{"text": s[2]}],
                "effectiveDateTime": s[3]
            }
        }
        bundle['entry'].append(obs)

    # Add mood logs
    for m in moods:
        obs = {
            "resource": {
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": "Mood Log"},
                "component": [
                    {"code": {"text": "mood_val"}, "valueQuantity": {"value": m[0]}},
                    {"code": {"text": "sleep_val"}, "valueQuantity": {"value": m[1]}},
                    {"code": {"text": "meds"}, "valueString": m[2] or ""},
                ],
                "note": [{"text": m[3] or ""}],
                "effectiveDateTime": m[4]
            }
        }
        bundle['entry'].append(obs)

    # Add Provenance entry describing the export
    if add_provenance:
        prov = {
            "resource": {
                "resourceType": "Provenance",
                "recorded": datetime.now(timezone.utc).isoformat(),
                "agent": [{"type": {"text": "author"}, "who": {"reference": f"Practitioner/{signer or 'system'}"}}],
                "entity": [{"role": "source", "what": {"reference": f"Patient/{username}"}}]
            }
        }
        bundle['entry'].append(prov)

    bundle_json = json.dumps(bundle, indent=2, default=str)

    # Validate bundle
    valid, errors = validate_fhir_bundle(bundle)
    if not valid:
        # still return a bundle but include validation problems under a top-level 'validation' key
        wrapped = {"bundle": json.loads(bundle_json), "validation": {"ok": False, "errors": errors}}
        bundle_json = json.dumps(wrapped, indent=2, default=str)

    if sign_bundle:
        return _sign_bundle(bundle_json)
    return bundle_json
