from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.hashes import SHA1
import base64

def generate_security_credentials(password: str, public_key_path: str) -> str:
    """
    Generate M-Pesa security credentials by encrypting the initiator password.

    Args:
        password (str): The initiator password to be encrypted.
        public_key_path (str): The file path to the M-Pesa public key certificate (X509 certificate).

    Returns:
        str: The base64-encoded security credentials.
    """
    try:
        # Load the public key from the certificate file
        with open(public_key_path, "rb") as cert_file:
            public_key = serialization.load_pem_public_key(cert_file.read())

        # Encrypt the password using the RSA algorithm with PKCS #1.5 padding
        encrypted_password = public_key.encrypt(
            password.encode("utf-8"),
            padding.PKCS1v15()
        )

        # Encode the encrypted password to a base64 string
        security_credentials = base64.b64encode(encrypted_password).decode("utf-8")

        return security_credentials

    except Exception as e:
        raise ValueError(f"Failed to generate security credentials: {e}")

# Example usage:
password = "#DennisMwangi0707"
public_key_path = "public_key.pem"
print(generate_security_credentials(password, public_key_path))