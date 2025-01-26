import os
import sqlite3
from pywebauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    PublicKeyCredentialRequestOptions,
)
from pywebauthn.helpers import generate_challenge

# Initialize SQLite database
DB_FILE = "database.db"
TABLE_NAME = "credentials"

def init_db():
    """Initialize the SQLite database and create the credentials table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            username TEXT PRIMARY KEY,
            credential_id TEXT NOT NULL,
            challenge TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Initialize the database on import
init_db()

def get_registration_options(username):
    """Generate registration options for the given username."""
    challenge = generate_challenge()
    creation_options = PublicKeyCredentialCreationOptions(
        challenge=challenge,
        rp={"name": "Streamlit WebAuthn App", "id": "localhost"},
        user={
            "id": os.urandom(16),
            "name": username,
            "displayName": username,
        },
        pubKeyCredParams=[{"alg": -7, "type": "public-key"}],
        timeout=60000,
        attestation="none",
    )

    # Save the challenge to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT OR REPLACE INTO {TABLE_NAME} (username, challenge)
        VALUES (?, ?)
    """, (username, challenge.hex()))
    conn.commit()
    conn.close()

    return creation_options

def save_credential(username, credential_id):
    """Save the registered credential ID for the user."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        UPDATE {TABLE_NAME}
        SET credential_id = ?
        WHERE username = ?
    """, (credential_id, username))
    conn.commit()
    conn.close()

def get_authentication_options(username):
    """Generate authentication options for the given username."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT credential_id, challenge
        FROM {TABLE_NAME}
        WHERE username = ?
    """, (username,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        raise ValueError("User not registered.")

    credential_id, challenge = result
    request_options = PublicKeyCredentialRequestOptions(
        challenge=bytes.fromhex(challenge),
        allowCredentials=[
            {
                "type": "public-key",
                "id": credential_id,
            }
        ],
        timeout=60000,
    )
    return request_options
