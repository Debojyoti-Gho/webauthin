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

# Helper to generate registration options
def generate_registration_options(user_id, username):
    challenge = base64.b64encode(uuid4().bytes).decode()  # Base64 encoded challenge
    return {
        "publicKey": {
            "rp": {
                "id": "localhost",  # Replace with your domain in production
                "name": "Streamlit WebAuthn App"
            },
            "user": {
                "id": base64.b64encode(user_id.encode()).decode(),  # Base64 encode user ID
                "name": username,
                "displayName": username
            },
            "challenge": challenge,  # Use the challenge here
            "pubKeyCredParams": [{"type": "public-key", "alg": -7}],  # ECDSA with SHA-256
            "authenticatorSelection": {"userVerification": "preferred"}
        },
        "challenge_base64": challenge,
        "credential_id_base64": base64.b64encode(user_id.encode()).decode()
    }

# WebAuthn Registration Process
def register_user(username, response):
    data = json.loads(response)
    credential_id = base64.b64encode(bytes(data["rawId"])).decode()  # Encode credential ID as base64
    public_key = json.dumps(data["response"]["attestationObject"])  # Store attestation object as JSON

    conn = sqlite3.connect("webauthn.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (id, username, credential_id, public_key) VALUES (?, ?, ?, ?)", 
                  (str(uuid4()), username, credential_id, public_key))
        conn.commit()
        return "Registration successful!"
    except sqlite3.IntegrityError:
        return "Username already exists. Please choose a different username."
    finally:
        conn.close()

# Streamlit Frontend
st.title("WebAuthn with SQLite")

tab1, tab2 = st.tabs(["Register", "Authenticate"])

# Registration Tab
with tab1:
    st.header("Register an Authenticator")
    username = st.text_input("Enter your username:")
    if username and st.button("Register"):
        user_id = str(uuid4())  # Generate user_id as a UUID string
        registration_options = generate_registration_options(user_id, username)

        js_code = f"""
        <script>
        async function registerAuthenticator() {{
            console.log("Registration started");
            const options = {json.dumps(registration_options)};
            options.publicKey.challenge = Uint8Array.from(atob(options.publicKey.challenge), c => c.charCodeAt(0));
            options.publicKey.user.id = Uint8Array.from(atob(options.publicKey.user.id), c => c.charCodeAt(0));

            try {{
                console.log("Calling navigator.credentials.create with options:", options);
                const credential = await navigator.credentials.create(options);
                console.log("Credential created:", credential);

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
                console.error("Registration failed:", err.message);
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

