import hashlib
import secrets
from pathlib import Path

# File setup
def file_setup():
    file_name = 'PasswordStorage'
    env_path = Path(f'../Storage/{file_name}.env')
    if not env_path.exists():
        env_path.write_text('')
        print(f"{file_name}.env file created")
        return False
    return True

# Hashing function
def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()

# Load credentials from .env
def load_credentials(filename="../Storage/PasswordStorage.env"):
    creds = {}
    with open(filename, "r") as file:
        for line in file:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                creds[key] = value
    return creds

# Save credentials to .env
def save_credentials(salt, hashed, filename="../Storage/PasswordStorage.env"):
    with open(filename, "w") as file:
        file.write(f"SALT={salt}\n")
        file.write(f"HASH={hashed}\n")
    print("Password saved. You only need to do this once.")

# Main logic
def main(input_password, salt):

    creds = load_credentials()

    if "SALT" in creds and "HASH" in creds:
        # Password already set — verify login
        input_hash = hash_password(input_password, creds[salt])
        if input_hash == creds["HASH"]:
            return True
        else:
            return False
    else:
        # No password yet — create one
        salt = secrets.token_hex(16)  # Secure random salt
        hashed = hash_password(input_password, salt)
        save_credentials(salt, hashed)
