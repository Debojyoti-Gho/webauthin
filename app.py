import streamlit as st
import json
from webauthn_backend import (
    get_registration_options,
    save_credential,
    get_authentication_options,
    verify_authentication_response,
)
from sqlite3 import OperationalError

# Initialize the database
from webauthn_backend import setup_database
setup_database()

st.title("Streamlit WebAuthn Demo")

# Username input
username = st.text_input("Enter your username")

# Registration
if st.button("Register"):
    if username:
        options = get_registration_options(username)
        st.write("Registration Options (Pass to WebAuthn API):")
        st.json(options.dict())  # Convert to a dictionary and display
        st.success("Pass the above options to your browser for registration and return the response.")
    else:
        st.error("Please provide a username.")

# Handle registration response
registration_response = st.text_area("Paste the registration response JSON here")
if st.button("Save Credential"):
    if username and registration_response:
        try:
            registration_data = json.loads(registration_response)
            save_credential(username, registration_data)
            st.success("Credential saved successfully!")
        except Exception as e:
            st.error(f"Error saving credential: {e}")
    else:
        st.error("Please provide both a username and registration response.")

# Authentication
if st.button("Login"):
    if username:
        options = get_authentication_options(username)
        st.write("Authentication Options (Pass to WebAuthn API):")
        st.json(options.dict())  # Convert to a dictionary and display
        st.success("Pass the above options to your browser for authentication and return the response.")
    else:
        st.error("Please provide a username.")

# Handle authentication response
authentication_response = st.text_area("Paste the authentication response JSON here")
if st.button("Verify Login"):
    if username and authentication_response:
        try:
            authentication_data = json.loads(authentication_response)
            if verify_authentication_response(username, authentication_data):
                st.success("Login successful!")
            else:
                st.error("Login failed. Could not verify the response.")
        except Exception as e:
            st.error(f"Error verifying login: {e}")
    else:
        st.error("Please provide both a username and authentication response.")
