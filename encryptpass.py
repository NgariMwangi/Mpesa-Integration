from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key

def encrypt_password(password, public_key_path):
    # Read the public key file
    with open(public_key_path, "rb") as key_file:
        public_key = load_pem_public_key(key_file.read())

    # Encrypt the password using the public key
    encrypted_password = public_key.encrypt(
        password.encode("utf-8"),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted_password

# Replace 'YourPassword' and 'path/to/public_key.pem' with your values
password = "#DennisMwangi"
public_key_path = "public_key.pem"

encrypted_password = encrypt_password(password, public_key_path)
print("Encrypted Password:", encrypted_password.hex())
