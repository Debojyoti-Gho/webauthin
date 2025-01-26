# WebAuthn Registration Script (JavaScript) for capturing fingerprint data
def webauthn_register_script():
    script = """
    <script>
        async function registerFingerprint() {
            try {
                // Generate WebAuthn registration options
                const publicKey = {
                    challenge: Uint8Array.from('someRandomChallenge123', c => c.charCodeAt(0)),
                    rp: { name: 'asas-beta-by-debojyotighosh.streamlit.app' },
                    user: {
                        id: new Uint8Array(16),
                        name: 'user@example.com',
                        displayName: 'Example User'
                    },
                    pubKeyCredParams: [{ type: 'public-key', alg: -7 }],
                    authenticatorAttachment: 'platform',
                    timeout: 60000,
                    userVerification: 'required'
                };

                // Call WebAuthn API to register the credential
                const credential = await navigator.credentials.create({ publicKey });

                // Store the registration response (public key and credential ID)
                localStorage.setItem('credentialId', credential.id);
                localStorage.setItem('publicKey', JSON.stringify(credential.response.attestationObject));

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


# Placeholder for WebAuthn integration script
def webauthn_script():
    script = """
    <script>
        async function authenticateFingerprint() {
            try {
                const publicKey = {
                    challenge: Uint8Array.from("YourServerChallenge", c => c.charCodeAt(0)), // Replace with a secure challenge
                    timeout: 60000,
                    userVerification: "required"
                };

                const assertion = await navigator.credentials.get({ publicKey });

                // Send the assertion back to server for verification
                const credentialId = assertion.id;
                const clientData = JSON.stringify(assertion.response.clientDataJSON);

                await fetch('/verify-authentication', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ credentialId, clientData })
                });

                document.getElementById('webauthn-result').innerHTML = 'Authentication successful!';
            } catch (error) {
                document.getElementById('webauthn-result').innerHTML = 'Authentication failed: ' + error;
            }
        }
    </script>
    <button onclick="authenticateFingerprint()">Authenticate Fingerprint</button>
    <p id="webauthn-result"></p>
    <input type="hidden" id="webauthn-status" name="webauthn-status" value="pending">
    """
    return script
