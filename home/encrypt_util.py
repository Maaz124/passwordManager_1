
import base64
import logging
import traceback
from django.conf import settings

from dotenv import load_dotenv, set_key  # Import the correct functions

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64
import logging
import traceback

# 1. Key Generation (AES-256)
# This will generate a 256-bit (32-byte) AES key and 128-bit (16-byte) IV.
def generate_key_and_iv():
    # Generate a random 256-bit AES key (32 bytes)
    key = os.urandom(32)  # AES-256 key size
    # Generate a random 128-bit IV (16 bytes)
    iv = os.urandom(16)  # AES block size (128 bits)
    return key, iv

def load_key_and_iv():
    key_b64 = os.getenv("AES_KEY")
    iv_b64 = os.getenv("AES_IV")
    
    if key_b64 and iv_b64:
        key = base64.urlsafe_b64decode(key_b64)
        iv = base64.urlsafe_b64decode(iv_b64)
        return key, iv
    else:
        print("Key and IV not found in .env.")
        return key_b64, iv_b64

def store_key_and_iv():
    # Check if the key and IV are already stored in .env
    if not os.getenv("AES_KEY") or not os.getenv("AES_IV"):
        # Generate new AES key and IV
        key, iv = generate_key_and_iv()

        # Convert key and IV to Base64 for easy storage in the .env file
        key_b64 = base64.urlsafe_b64encode(key).decode('ascii')
        iv_b64 = base64.urlsafe_b64encode(iv).decode('ascii')

        # Add them to the .env file
        set_key(".env", "AES_KEY", key_b64)
        set_key(".env", "AES_IV", iv_b64)
        print("AES Key and IV have been generated and stored in .env.")
    else:
        print("AES Key and IV are already present in .env.")

store_key_and_iv()
key,iv=load_key_and_iv()

# 2. Encryption Function


def encrypt(pas):
    try:
        # Convert the password to bytes (if it's a string)
        pas = str(pas).encode('utf-8')

        # Create AES cipher in CBC mode using the key and IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Pad the password to make its length a multiple of AES block size (16 bytes)
        padder = padding.PKCS7(128).padder()
        padded_pas = padder.update(pas) + padder.finalize()

        # Encrypt the padded password
        encrypted_pas = encryptor.update(padded_pas) + encryptor.finalize()

        # Base64 encode the encrypted password to store or transmit as a string
        encrypted_pas_b64 = base64.urlsafe_b64encode(encrypted_pas).decode("ascii")

        return encrypted_pas_b64

    except Exception as e:
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None

# 3. Decryption Function
def decrypt(pas):
    try:
        # Decode the Base64 encrypted password
        pas = base64.urlsafe_b64decode(pas)

        # Create AES cipher in CBC mode using the key and IV
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the password
        decrypted_pas = decryptor.update(pas) + decryptor.finalize()

        # Unpad the decrypted password
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_pas = unpadder.update(decrypted_pas) + unpadder.finalize()

        # Convert decrypted bytes to string
        return unpadded_pas.decode('utf-8')

    except Exception as e:
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None

# Example of how to use this in your application

# Generate the AES key and IV (only once, then store securely)

print(f"Generated AES Key: {base64.urlsafe_b64encode(key).decode('ascii')}")
print(f"Generated AES IV: {base64.urlsafe_b64encode(iv).decode('ascii')}")

# Example password to encrypt
original_password = "my_secret_password"

# Encrypt the password
encrypted_password = encrypt(original_password)
print(f"Encrypted Password: {encrypted_password}")

# Decrypt the password back
decrypted_password = decrypt(encrypted_password)
print(f"Decrypted Password: {decrypted_password}")
