import os
import sqlite3
from webauthn import generate_registration_options, generate_authentication_options
from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    PublicKeyCredentialRequestOptions,
    RegistrationCredential,
    AuthenticationCredential,
)
from webauthn.helpers.exceptions import InvalidRegistrationResponse, InvalidAuthenticationResponse

# Database setup
DB_FILE = "credentials.db"
TABLE_NAME = "credentials"

def setup_database():
    """Create the database and table if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            credential_id TEXT NOT NULL UNIQUE,
            public_key TEXT NOT NULL,
            sign_count INTEGER NOT NULL,
            challenge TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

def get_registration_options(username):
    """Generate registration options for WebAuthn."""
    challenge = os.urandom(32).hex()
    options = generate_registration_options(
        rp_id="localhost",
        rp_name="Streamlit WebAuthn App",
        user_id=username.encode("utf-8"),
        user_name=username,
        challenge=challenge,
    )

    # Save challenge to DB
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        f"INSERT OR REPLACE INTO {TABLE_NAME} (username, challenge) VALUES (?, ?)",
        (username, challenge),
    )
    conn.commit()
    conn.close()

    return options

def save_credential(username, registration_response):
    """Save a credential to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Retrieve challenge from DB
        cursor.execute(
            f"SELECT challenge FROM {TABLE_NAME} WHERE username = ?", (username,)
        )
        result = cursor.fetchone()
        if not result:
            raise ValueError("Challenge not found for the given username.")
        challenge = result[0]

        # Validate registration response
        credential = RegistrationCredential.parse_obj(registration_response)
        verified_registration = credential.verify(
            expected_rp_id="localhost",
            expected_origin="http://localhost:8501",
            expected_challenge=challenge,
        )

        # Save credential to DB
        cursor.execute(
            f"""
            INSERT INTO {TABLE_NAME} (username, credential_id, public_key, sign_count, challenge)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                username,
                verified_registration.credential_id,
                verified_registration.credential_public_key,
                verified_registration.sign_count,
                challenge,
            ),
        )
        conn.commit()

    finally:
        conn.close()

def get_authentication_options(username):
    """Generate authentication options for WebAuthn."""
    challenge = os.urandom(32).hex()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Fetch the credential ID for the user
    cursor.execute(
        f"SELECT credential_id FROM {TABLE_NAME} WHERE username = ?", (username,)
    )
    result = cursor.fetchone()
    if not result:
        raise ValueError("No credential found for the given username.")
    credential_id = result[0]

    options = generate_authentication_options(
        rp_id="localhost",
        challenge=challenge,
        allow_credentials=[credential_id],
    )

    # Save challenge to DB
    cursor.execute(
        f"UPDATE {TABLE_NAME} SET challenge = ? WHERE username = ?", (challenge, username)
    )
    conn.commit()
    conn.close()

    return options

def verify_authentication_response(username, authentication_response):
    """Verify the authentication response."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Retrieve credential and challenge
        cursor.execute(
            f"""
            SELECT credential_id, public_key, sign_count, challenge
            FROM {TABLE_NAME}
            WHERE username = ?
            """,
            (username,),
        )
        result = cursor.fetchone()
        if not result:
            raise ValueError("Credential not found for the given username.")
        credential_id, public_key, stored_sign_count, challenge = result

        # Verify the response
        credential = AuthenticationCredential.parse_obj(authentication_response)
        verified_authentication = credential.verify(
            expected_rp_id="localhost",
            expected_origin="http://localhost:8501",
            expected_challenge=challenge,
            credential_public_key=public_key,
            credential_current_sign_count=stored_sign_count,
        )

        # Update sign count in the DB
        cursor.execute(
            f"UPDATE {TABLE_NAME} SET sign_count = ? WHERE username = ?",
            (verified_authentication.new_sign_count, username),
        )
        conn.commit()

        return True

    except InvalidAuthenticationResponse:
        return False

    finally:
        conn.close()
