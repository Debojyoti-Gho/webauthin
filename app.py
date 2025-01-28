import streamlit as st
import sqlite3
import base64
import json
from uuid import uuid4

# Database initialization
def init_db():
    conn = sqlite3.connect("webauthn.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            credential_id TEXT,
            public_key TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper to generate authentication options
def generate_authentication_options(credential_id):
    challenge = base64.b64encode(uuid4().bytes).decode()  # Base64 encoded challenge
    return {
        "publicKey": {
            "rpId": "localhost",  # Replace with your domain in production
            "challenge": challenge,
            "userVerification": "preferred",
            "allowCredentials": [
                {"type": "public-key", "id": base64.b64encode(credential_id.encode()).decode()}
            ]
        },
        "challenge_base64": challenge,
        "credential_id_base64": base64.b64encode(credential_id.encode()).decode()
    }

# WebAuthn Authentication Process
def authenticate_user(username, response):
    conn = sqlite3.connect("webauthn.db")
    c = conn.cursor()
    c.execute("SELECT credential_id FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()

    if not row:
        return "User not found!"

    credential_id = base64.b64decode(row[0])  # Decode credential ID from base64
    data = json.loads(response)

    # Validate the response (this is a placeholder, actual validation logic should be added)
    if data.get("id") and bytes(data["id"]) == credential_id:
        return "Authentication successful!"
    else:
        return "Authentication failed!"

# Streamlit Frontend
st.title("WebAuthn with SQLite")

tab1, tab2 = st.tabs(["Register", "Authenticate"])

# Registration Tab
with tab1:
    st.header("Register an Authenticator")
    username = st.text_input("Enter your username:")
    if username and st.button("Register"):
        user_id = str(uuid4())
        registration_options = generate_registration_options(user_id, username)

        js_code = f"""
        <script>
        async function registerAuthenticator() {{
            const options = {json.dumps(registration_options)};
            options.publicKey.challenge = Uint8Array.from(atob(options.publicKey.challenge), c => c.charCodeAt(0));
            options.publicKey.user.id = Uint8Array.from(atob(options.publicKey.user.id), c => c.charCodeAt(0));

            try {{
                const credential = await navigator.credentials.create(options);
                const response = {{
                    id: credential.id,
                    rawId: Array.from(new Uint8Array(credential.rawId)),
                    type: credential.type,
                    response: {{
                        clientDataJSON: Array.from(new Uint8Array(credential.response.clientDataJSON)),
                        attestationObject: Array.from(new Uint8Array(credential.response.attestationObject))
                    }}
                }};
                document.getElementById("response").value = JSON.stringify(response);
                document.getElementById("form").submit();
            }} catch (err) {{
                alert("Registration failed: " + err.message);
            }}
        }}
        registerAuthenticator();
        </script>
        <form id="form" method="post">
            <input type="hidden" id="response" name="response">
        </form>
        """
        st.markdown(js_code, unsafe_allow_html=True)

    # Handle WebAuthn Response
    response = st.text_area("Paste the WebAuthn response here:")
    if response and st.button("Submit Registration"):
        message = register_user(username, response)
        st.success(message)

# Authentication Tab
with tab2:
    st.header("Authenticate with your Authenticator")
    username = st.text_input("Enter your username:", key="auth_username")
    if username and st.button("Authenticate"):
        conn = sqlite3.connect("webauthn.db")
        c = conn.cursor()
        c.execute("SELECT credential_id FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()

        if not row:
            st.error("User not found!")
        else:
            credential_id = base64.b64decode(row[0])
            authentication_options = generate_authentication_options(credential_id)

            js_code = f"""
            <script>
            async function authenticate() {{
                const options = {json.dumps(authentication_options)};
                options.publicKey.challenge = Uint8Array.from(atob(options.publicKey.challenge), c => c.charCodeAt(0));
                options.publicKey.allowCredentials = options.publicKey.allowCredentials.map(cred => {{
                    return {{
                        id: Uint8Array.from(atob(cred.id), c => c.charCodeAt(0)),
                        type: cred.type,
                        transports: cred.transports
                    }};
                }});

                try {{
                    const assertion = await navigator.credentials.get(options);
                    const response = {{
                        id: assertion.id,
                        rawId: Array.from(new Uint8Array(assertion.rawId)),
                        type: assertion.type,
                        response: {{
                            clientDataJSON: Array.from(new Uint8Array(assertion.response.clientDataJSON)),
                            authenticatorData: Array.from(new Uint8Array(assertion.response.authenticatorData)),
                            signature: Array.from(new Uint8Array(assertion.response.signature))
                        }}
                    }};
                    document.getElementById("auth_response").value = JSON.stringify(response);
                    document.getElementById("auth_form").submit();
                }} catch (err) {{
                    alert("Authentication failed: " + err.message);
                }}
            }}
            authenticate();
            </script>
            <form id="auth_form" method="post">
                <input type="hidden" id="auth_response" name="auth_response">
            </form>
            """
            st.markdown(js_code, unsafe_allow_html=True)

    # Handle WebAuthn Response
    auth_response = st.text_area("Paste the WebAuthn response here (Authentication):")
    if auth_response and st.button("Submit Authentication"):
        message = authenticate_user(username, auth_response)
        st.success(message)
