import streamlit as st
import requests

# Frontend: Display the WebAuthn HTML and JavaScript
webauthn_registration_html = """
    <html>
        <head>
            <script>
                if (window.PublicKeyCredential) {
                    console.log("WebAuthn supported!");

                    async function registerAuthenticator() {
                        const options = {
                            publicKey: {
                                rp: { id: "cosmosclownstore.com", name: "Cosmo’s Clown Store" },
                                user: { id: "1234", name: "krusty@example.com", displayName: "Krusty The Clown" },
                                challenge: "random-challenge",
                                pubKeyCredParams: [ { type: "public-key", alg: -7 }],
                                authenticatorSelection: {}
                            }
                        };

                        try {
                            const credential = await navigator.credentials.create(options);
                            console.log(credential);
                            // Send this credential data to your backend for processing
                            // Use fetch to send credential to your backend for storage/validation
                            fetch("/register", {
                                method: 'POST',
                                body: JSON.stringify(credential),
                                headers: {
                                    'Content-Type': 'application/json'
                                }
                            })
                            .then(response => response.json())
                            .then(data => console.log("Registration response", data));
                        } catch (error) {
                            console.error("Error during registration:", error);
                        }
                    }

                    async function authenticateUser() {
                        const credentialId = "credential_id_from_registration";

                        const options = {
                            publicKey: {
                                rpId: "cosmosclownstore.com",
                                challenge: "random-challenge",
                                userVerification: "preferred",
                                allowCredentials: [{ type: "public-key", id: credentialId }]
                            }
                        };

                        try {
                            const credential = await navigator.credentials.get(options);
                            console.log(credential);
                            // Send authentication data to your backend for verification
                            fetch("/authenticate", {
                                method: 'POST',
                                body: JSON.stringify(credential),
                                headers: {
                                    'Content-Type': 'application/json'
                                }
                            })
                            .then(response => response.json())
                            .then(data => console.log("Authentication response", data));
                        } catch (error) {
                            console.error("Error during authentication:", error);
                        }
                    }
                } else {
                    alert("WebAuthn is not supported in this browser.");
                }
            </script>
        </head>
        <body>
            <h1>WebAuthn Authentication</h1>
            <button onclick="registerAuthenticator()">Register Biometric Authenticator</button>
            <button onclick="authenticateUser()">Login with Biometric</button>
        </body>
    </html>
"""

# Display the WebAuthn registration and authentication UI
st.components.v1.html(webauthn_registration_html)

# Backend: Define Streamlit server-side functionality for registration and authentication
@st.cache
def register_webauthn(credential_data):
    # Logic to handle the registration, e.g., store credential data in your backend
    # This part would typically involve storing the attestationObject, and clientDataJSON in your database
    return {"status": "success", "message": "Registration successful!"}

@st.cache
def authenticate_webauthn(credential_data):
    # Logic to handle the authentication, e.g., verify the credentials against stored data
    return {"status": "success", "message": "Authentication successful!"}

# Server-side routes to handle POST requests
def register():
    if st.request.method == 'POST':
        credential_data = st.request.json()
        result = register_webauthn(credential_data)
        st.write(result)

def authenticate():
    if st.request.method == 'POST':
        credential_data = st.request.json()
        result = authenticate_webauthn(credential_data)
        st.write(result)

# Streamlit setup for HTTP methods (requests to backend) 
register()
authenticate()
