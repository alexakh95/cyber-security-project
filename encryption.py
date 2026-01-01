from argon2 import PasswordHasher
import bcrypt, hashlib, os
import yaml
from dotenv import load_dotenv
load_dotenv()

with open("config.yaml", "r") as f:
    APP_CONFIG = yaml.safe_load(f)

PEPPER = APP_CONFIG["config"]["pepper"]

# Get the pepper
pepper_bytes = os.getenv("PEPPER_VAL", "").encode() if PEPPER else b""
    
SALT = APP_CONFIG["config"]["salt"]
HASH_METHOD = APP_CONFIG["config"]["hash"]

def_hash = PasswordHasher(time_cost=1, memory_cost=65536, parallelism=1)



def hash_password(password):
    
    password_bytes = password.encode()
    salt_hex = None  # Default if no salt is used

    # 2. Hashing Logic
    if HASH_METHOD == "sha256":
        data = password_bytes
        if SALT:
            salt_raw = os.urandom(16)
            salt_hex = salt_raw.hex()
            data += salt_raw
        
        data += pepper_bytes # Add pepper last
        hashed = hashlib.sha256(data).hexdigest()

    elif HASH_METHOD == "bcrypt":
        # Best practice for pepper + bcrypt: 
        # Hash the combo with SHA256 first to avoid the 72-character limit
        payload = password_bytes + pepper_bytes
        hashed = bcrypt.hashpw(payload, bcrypt.gensalt(rounds=12)).decode('utf-8')

    elif HASH_METHOD == "argon2id":
        # Argon2 handles its own salt; we just provide the peppered string
        payload = password + (pepper_bytes.decode() if PEPPER else "")
        hashed = def_hash.hash(payload)

    else:
        # Plaintext
        hashed = password

    # Always return (hash, salt) so your DB saving code is consistent
    return hashed, salt_hex

def verify_password(password, stored_hash, salt=None):
    password_bytes = password.encode()
    
    if HASH_METHOD == "sha256":
        # Combine components
        data = password_bytes
        if SALT and salt:
            data += bytes.fromhex(salt)
        data += pepper_bytes
        
        current_hash = hashlib.sha256(data).hexdigest()
        
        return current_hash ==  stored_hash
    
    elif HASH_METHOD == "bcrypt":
        # Note: bcrypt has a 72-character limit. 
        # Adding a long pepper might truncate the password.
        # Pre-hashing the password+pepper is a common workaround.
        payload = password_bytes + pepper_bytes
        return bcrypt.checkpw(payload, stored_hash.encode('utf-8'))
        
    elif HASH_METHOD == "argon2id":
        # Argon2 handles its own salting internally
        payload = password + (pepper_bytes.decode() if PEPPER else "")
        try:
            return def_hash.verify(stored_hash, payload)
        except Exception:
            return False
            
    else:
        return password == stored_hash
