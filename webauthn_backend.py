import os
import sqlite3
from webauthn import generate_registration_options, generate_authentication_options

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
    challenge = os.urandom(32).hex()
    options = generate_registration_options(
        rp_id="localhost",
        rp_name="Streamlit WebAuthn App",
        user_id=username,
        user_name=username,
        user_display_name=username,
        challenge=challenge,
    )

    # Save the challenge to the database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"""
        INSERT OR REPLACE INTO {TABLE_NAME} (username, challenge)
        VALUES (?, ?)
    """, (username, challenge))
    conn.commit()
    conn.close()

    return options


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
    options = generate_authentication_options(
        rp_id="localhost",
        challenge=challenge,
        allow_credentials=[{"id": credential_id, "type": "public-key"}],
    )

    return options
