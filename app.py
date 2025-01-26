import streamlit as st
import sqlite3
import os
from webauthn_backend import setup_database, save_credential

# Initialize the database
setup_database()

st.title("WebAuthn Fingerprint Authentication")

# Serve WebAuthn JavaScript for registration
def webauthn_register_script():
    script = """
    <script>
        async function registerFingerprint() {
            try {
                // Call the backend to get registration options
                const response = await fetch('/generate-registration-options');
                const publicKey = await response.json();

                // Use WebAuthn API to register
                const credential = await navigator.credentials.create({ publicKey });

                // Store the response
                const credentialId = credential.id;
                const attestation = JSON.stringify(credential.response.attestationObject);

                // Send response back to server
                await fetch('/verify-registration', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ credentialId, attestation })
                });

                document.getElementById('registration-result').innerHTML = 'Registration successful!';
            } catch (error) {
                document.getElementById('registration-result').innerHTML = 'Registration failed: ' + error;
            }
        }
    </script>
    <button onclick="registerFingerprint()">Register Fingerprint</button>
    <p id="registration-result"></p>
    """
    return script


# Serve WebAuthn JavaScript for authentication
def webauthn_authenticate_script():
    script = """
    <script>
        async function authenticateFingerprint() {
            try {
                // Call the backend to get authentication options
                const response = await fetch('/generate-authentication-options');
                const publicKey = await response.json();

                // Use WebAuthn API to authenticate
                const assertion = await navigator.credentials.get({ publicKey });

                // Send the assertion back to server for verification
                const credentialId = assertion.id;
                const clientData = JSON.stringify(assertion.response.clientDataJSON);

                await fetch('/verify-authentication', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ credentialId, clientData })
                });

                document.getElementById('authentication-result').innerHTML = 'Authentication successful!';
            } catch (error) {
                document.getElementById('authentication-result').innerHTML = 'Authentication failed: ' + error;
            }
        }
    </script>
    <button onclick="authenticateFingerprint()">Authenticate Fingerprint</button>
    <p id="authentication-result"></p>
    """
    return script


# Embedding JavaScript into Streamlit
st.markdown(webauthn_register_script(), unsafe_allow_html=True)
st.markdown(webauthn_authenticate_script(), unsafe_allow_html=True)
