from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    PublicKeyCredentialRequestOptions,
)
from webauthn import generate_registration_options, generate_authentication_options
import sqlite3
import os

DB_FILE = "credentials.db"

def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credentials (
            username TEXT PRIMARY KEY,
            credential_id TEXT NOT NULL,
            public_key TEXT NOT NULL,
            challenge TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def generate_registration_options(username):
    challenge = os.urandom(32).hex()
    options = generate_registration_options(
        rp_id="localhost",
        rp_name="Streamlit WebAuthn App",
        user_id=username.encode("utf-8"),
        user_name=username,
        challenge=challenge
    )
    save_challenge(username, challenge)
    return options

def save_challenge(username, challenge):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO credentials (username, challenge) VALUES (?, ?)", (username, challenge))
    conn.commit()
    conn.close()

# Handle credential saving
def save_credential(username, registration_response):
    pass  # Implement the save logic
