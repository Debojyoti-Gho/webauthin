import streamlit as st
import json
from webauthn_backend import (
    get_registration_options,
    save_credential,
    get_authentication_options,
)

st.title("WebAuthn Fingerprint Authentication")

# State management
if "username" not in st.session_state:
    st.session_state["username"] = ""

if "register_mode" not in st.session_state:
    st.session_state["register_mode"] = False

username = st.text_input("Enter your username", key="username")

# Registration
if st.button("Register"):
    if username:
        options = get_registration_options(username)
        st.session_state["register_mode"] = True
        st.write("Registration Options (Pass to WebAuthn API):")
        st.json(json.loads(options.json(indent=2)))

        st.success("Pass the above options to your browser for registration.")

if st.session_state.get("register_mode", False):
    credential_id = st.text_input("Enter the credential ID returned by WebAuthn API")
    if st.button("Save Credential"):
        if credential_id:
            save_credential(username, credential_id)
            st.session_state["register_mode"] = False
            st.success(f"Registration complete for user: {username}.")

# Login
if st.button("Login"):
    if username:
        try:
            options = get_authentication_options(username)
            st.write("Authentication Options (Pass to WebAuthn API):")
            st.json(json.loads(options.json(indent=2)))

            st.success("Pass the above options to your browser for authentication.")
        except ValueError as e:
            st.error(str(e))

# JavaScript for WebAuthn API (inline for simplicity)
st.markdown("""
<script>
async function register() {
    const options = JSON.parse(prompt("Paste the registration options:"));
    const credential = await navigator.credentials.create({
        publicKey: options,
    });

    const credentialID = btoa(
        String.fromCharCode(...new Uint8Array(credential.rawId))
    );

    alert(`Credential registered! Credential ID: ${credentialID}`);
    console.log(credential);
}

async function login() {
    const options = JSON.parse(prompt("Paste the authentication options:"));
    const credential = await navigator.credentials.get({
        publicKey: options,
    });

    console.log(credential);
    alert("Authentication successful!");
}
</script>
""", unsafe_allow_html=True)
