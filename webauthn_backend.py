import os
import sqlite3
from webauthn import generate_registration_options, generate_authentication_options, verify_registration_response, verify_authentication_response

DB_FILE = "webauthn.db"
TABLE_NAME = "credentials"
CHALLENGE_TABLE = "registration_challenges"

def setup_database():
    """Create necessary tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            username TEXT PRIMARY KEY,
            credential_id TEXT NOT NULL,
            public_key TEXT NOT NULL
        );
    """)
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {CHALLENGE_TABLE} (
            username TEXT PRIMARY KEY,
            challenge TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def get_registration_options(username):
    """Generate registration options for the given username."""
    challenge = os.urandom(32).hex()
    options = generate_registration_options(
        rp_id="localhost",
        rp_name="Streamlit WebAuthn App",
        user_id=username.encode('utf-8'),  # Convert to bytes
        user_name=username,
        user_display_name=username,
        challenge=challenge,
    )

    # Save the challenge to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT OR REPLACE INTO {CHALLENGE_TABLE} (username, challenge)
        VALUES (?, ?)
    """, (username, challenge))
    conn.commit()
    conn.close()

    return options

def save_credential(username, credential):
    """Save a completed credential to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT INTO {TABLE_NAME} (username, credential_id, public_key)
        VALUES (?, ?, ?)
    """, (username, credential["id"], credential["response"]["attestationObject"]))
    conn.commit()
    conn.close()

def get_authentication_options(username):
    """Generate authentication options for the given username."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT challenge FROM {CHALLENGE_TABLE} WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"No challenge found for username: {username}")

    challenge = row[0]
    options = generate_authentication_options(
        rp_id="localhost",
        user_verification="preferred",
        challenge=challenge,
    )
    return options

def verify_authentication_response(username, authentication_data):
    """Verify an authentication response."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT public_key FROM {TABLE_NAME} WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"No credentials found for username: {username}")

    public_key = row[0]
    verified = verify_authentication_response(
        credential=authentication_data,
        expected_rp_id="localhost",
        expected_origin="http://localhost",
        credential_public_key=public_key,
    )
    return verified
