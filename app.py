import streamlit as st
import json
import random
import string
import requests
import streamlit.components.v1 as components

# Function to generate random challenge
def generate_random_challenge():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=64))

# Function to create WebAuthn registration options
def get_registration_options():
    challenge = generate_random_challenge()  # Generate random challenge
    options = {
        "publicKey": {
            "rp": {
                "id": "cosmosclownstore.com",
                "name": "Cosmo’s Clown Store"
            },
            "user": {
                "id": "1234",  # Example user ID, replace with actual user identifier
                "name": "krusty@example.com",
                "displayName": "Krusty The Clown"
            },
            "challenge": challenge,  # Use random challenge
            "pubKeyCredParams": [{"type": "public-key", "alg": -7}],  # ES256
            "authenticatorSelection": {}
        }
    }
    return json.dumps(options)

# Function to create WebAuthn authentication options
def get_authentication_options(credential_id):
    challenge = generate_random_challenge()  # Generate random challenge
    options = {
        "publicKey": {
            "rpId": "cosmosclownstore.com",
            "challenge": challenge,  # Use random challenge
            "userVerification": "preferred",
            "allowCredentials": [{
                "type": "public-key",
                "id": credential_id
            }]
        }
    }
    return json.dumps(options)

# Function to inject JavaScript for WebAuthn registration
def inject_js_register(js_code):
    components.html(f"""
        <script>
        {js_code}
        </script>
    """)

# Function to inject JavaScript for WebAuthn authentication
def inject_js_authenticate(js_code):
    components.html(f"""
        <script>
        {js_code}
        </script>
    """)

# Registration flow
def register_user():
    options = get_registration_options()

    # Display the registration options as JSON for WebAuthn
    st.write("Registration options:", options)

    # JavaScript for handling WebAuthn registration
    register_js = f"""
    if (window.PublicKeyCredential) {{
        const options = {options};
        navigator.credentials.create(options).then(function(response) {{
            console.log(response);  // Handle the response here
            alert('Registration Successful!');
            // In real-world, you would store response.clientDataJSON and response.attestationObject in a database
        }}).catch(function(error) {{
            console.error(error);
        }});
    }} else {{
        alert("WebAuthn not supported. Falling back to password authentication.");
    }}
    """
    inject_js_register(register_js)

# Authentication flow
def authenticate_user():
    # Simulate getting a credential ID after registration
    credential_id = "some_credential_id"  # This should be retrieved from your database

    options = get_authentication_options(credential_id)

    # Display the authentication options as JSON for WebAuthn
    st.write("Authentication options:", options)

    # JavaScript for handling WebAuthn authentication
    authenticate_js = f"""
    if (window.PublicKeyCredential) {{
        const options = {options};
        navigator.credentials.get(options).then(function(response) {{
            console.log(response);  // Handle the response here
            alert('Authentication Successful!');
            // In real-world, you would compare the response.clientDataJSON to the expected challenge
        }}).catch(function(error) {{
            console.error(error);
        }});
    }} else {{
        alert("WebAuthn not supported. Falling back to password authentication.");
    }}
    """
    inject_js_authenticate(authenticate_js)

# Main page UI
def main():
    st.title("Biometric Authentication App")

    # Sidebar for navigation
    choice = st.sidebar.radio("Select Action", ["Register", "Login"])

    if choice == "Register":
        st.write("#### Register your biometric data")
        register_user()
    elif choice == "Login":
        st.write("#### Login with your biometric data")
        authenticate_user()

if __name__ == "__main__":
    main()
