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
def register_webauthn(credential_data):
    # Logic to handle the registration, e.g., store credential data in your backend
    # This part would typically involve storing the attestationObject, and clientDataJSON in your database
    return {"status": "success", "message": "Registration successful!"}

def authenticate_webauthn(credential_data):
    # Logic to handle the authentication, e.g., verify the credentials against stored data
    return {"status": "success", "message": "Authentication successful!"}

# Server-side actions triggered by user interaction
if st.button("Register Biometric Authenticator"):
    # Call the WebAuthn registration function when the button is pressed
    credential_data = {}  # Replace with actual credential data from frontend
    result = register_webauthn(credential_data)
    st.write(result)

if st.button("Login with Biometric"):
    # Call the WebAuthn authentication function when the button is pressed
    credential_data = {}  # Replace with actual credential data from frontend
    result = authenticate_webauthn(credential_data)
    st.write(result)
