import streamlit as st
import requests
import json

# Flask Backend URL (Update with the deployed URL on Render)
BACKEND_URL = "https://backend-flask-webauthin.onrender.com"  # Change this to your Render URL

# Function to trigger user registration (WebAuthn)
def register_user(user_id, user_name):
    response = requests.post(f"{BACKEND_URL}/register_options", json={"user_id": user_id, "user_name": user_name})
    options = response.json()
    
    st.session_state.registration_options = options

    # Trigger WebAuthn registration in the browser using JavaScript
    st.components.v1.html(f"""
        <script>
            const options = {json.dumps(options)};
            navigator.credentials.create({{
                publicKey: options
            }}).then(response => {{
                fetch("{BACKEND_URL}/register_response", {{
                    method: 'POST',
                    body: JSON.stringify({
                        user_id: "{user_id}",
                        response_data: response
                    }),
                    headers: {{
                        'Content-Type': 'application/json'
                    }}
                }});
            }}).catch(err => {{
                console.log("Registration failed: ", err);
            }});
        </script>
    """, height=0)

# Function to trigger user login (WebAuthn)
def login_user(user_id):
    response = requests.post(f"{BACKEND_URL}/login_options", json={"user_id": user_id})
    options = response.json()
    
    st.session_state.authentication_options = options

    # Trigger WebAuthn login in the browser using JavaScript
    st.components.v1.html(f"""
        <script>
            const options = {json.dumps(options)};
            navigator.credentials.get({{
                publicKey: options
            }}).then(response => {{
                fetch("{BACKEND_URL}/login_response", {{
                    method: 'POST',
                    body: JSON.stringify({
                        user_id: "{user_id}",
                        response_data: response
                    }),
                    headers: {{
                        'Content-Type': 'application/json'
                    }}
                }});
            }}).catch(err => {{
                console.log("Login failed: ", err);
            }});
        </script>
    """, height=0)

# Streamlit UI for Register and Login
st.title("WebAuthn Fingerprint Authentication")
user_id = st.text_input("Enter User ID")
user_name = st.text_input("Enter User Name")

if st.button("Register User"):
    register_user(user_id, user_name)
    st.success("Registration process initiated!")

if st.button("Login User"):
    login_user(user_id)
    st.success("Login process initiated!")
