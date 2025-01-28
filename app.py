import streamlit as st
import sqlite3
import json
from uuid import uuid4
import base64

# Database setup
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,  -- UUID
    username TEXT UNIQUE NOT NULL,  -- Username or email
    credential_id TEXT NOT NULL  -- Credential ID from WebAuthn response
)
""")
conn.commit()

# Streamlit App
st.title("WebAuthn with SQLite")

st.sidebar.header("Actions")
option = st.sidebar.selectbox("Choose an action", ["Register", "Authenticate"])

# Step 1: Define helper functions
def generate_registration_options(user_id, username):
    """Generate options for WebAuthn registration."""
    return {
        "publicKey": {
            "rp": {
                "id": "localhost",  # Use your domain in production
                "name": "Streamlit WebAuthn App"
            },
            "user": {
                "id": base64.b64encode(user_id.encode()).decode(),  # Encode to base64 string
                "name": username,
                "displayName": username
            },
            "challenge": base64.b64encode(uuid4().hex.encode()).decode(),  # Encode challenge to base64 string
            "pubKeyCredParams": [{"type": "public-key", "alg": -7}],  # ECDSA with SHA-256
            "authenticatorSelection": {"userVerification": "preferred"}
        }
    }

def generate_authentication_options(credential_id):
    """Generate options for WebAuthn authentication."""
    return {
        "publicKey": {
            "rpId": "localhost",  # Use your domain in production
            "challenge": base64.b64encode(uuid4().hex.encode()).decode(),  # Encode challenge to base64 string
            "userVerification": "preferred",
            "allowCredentials": [{"type": "public-key", "id": credential_id}]
        }
    }

# Step 2: Handle Registration
if option == "Register":
    st.header("Register an Authenticator")
    
    username = st.text_input("Enter your username:")
    if st.button("Register"):
        if username:
            user_id = uuid4().hex  # Generate a unique ID for the user
            registration_options = generate_registration_options(user_id, username)

            # Embed WebAuthn registration JS in Streamlit
            js_code = f"""
            <script>
            async function registerAuthenticator() {{
                const options = {json.dumps(registration_options)};
                try {{
                    const credential = await navigator.credentials.create(options);
                    document.getElementById("response").value = JSON.stringify(credential);
                }} catch (err) {{
                    document.getElementById("response").value = JSON.stringify({{"error": err.message}});
                }}
            }}
            registerAuthenticator();
            </script>
            <input type="hidden" id="response" name="response">
            """
            st.components.v1.html(js_code, height=300)

            # Capture WebAuthn response
            webauthn_response = st.text_area("Paste the WebAuthn response here:")
            if st.button("Submit Registration"):
                try:
                    response = json.loads(webauthn_response)
                    if "error" in response:
                        st.error(f"Registration failed: {response['error']}")
                    else:
                        # Save user and credential ID in SQLite
                        credential_id = response['rawId']
                        try:
                            cursor.execute("INSERT INTO users (id, username, credential_id) VALUES (?, ?, ?)", 
                                           (user_id, username, credential_id))
                            conn.commit()
                            st.success("Registration successful!")
                            st.write(f"Saved credential ID: {credential_id}")
                        except sqlite3.IntegrityError:
                            st.error("Username already exists. Please choose a different username.")
                except Exception as e:
                    st.error(f"Failed to process response: {e}")

# Step 3: Handle Authentication
if option == "Authenticate":
    st.header("Authenticate with Biometrics")

    username = st.text_input("Enter your username to authenticate:")
    if st.button("Authenticate"):
        cursor.execute("SELECT credential_id FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            credential_id = row[0]
            authentication_options = generate_authentication_options(credential_id)

            # Embed WebAuthn authentication JS in Streamlit
            js_code = f"""
            <script>
            async function authenticate() {{
                const options = {json.dumps(authentication_options)};
                try {{
                    const assertion = await navigator.credentials.get(options);
                    document.getElementById("response").value = JSON.stringify(assertion);
                }} catch (err) {{
                    document.getElementById("response").value = JSON.stringify({{"error": err.message}});
                }}
            }}
            authenticate();
            </script>
            <input type="hidden" id="response" name="response">
            """
            st.components.v1.html(js_code, height=300)

            # Capture WebAuthn response
            webauthn_response = st.text_area("Paste the WebAuthn response here:")
            if st.button("Submit Authentication"):
                try:
                    response = json.loads(webauthn_response)
                    if "error" in response:
                        st.error(f"Authentication failed: {response['error']}")
                    else:
                        st.success("Authentication successful!")
                        st.write("Authentication response:")
                        st.json(response)
                except Exception as e:
                    st.error(f"Failed to process response: {e}")
        else:
            st.error("User not found. Please register first.")
