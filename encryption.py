from argon2 import PasswordHasher
import bcrypt, hashlib, os

def_hash = PasswordHasher(time_cost=1, memory_cost=65536, parallelism=1)


def hash_password(password, method, use_salt=False):

    if method == "sha256":
        if use_salt:
            salt = os.urandom(16)
            # Return hash and hex-encoded salt for storage
            return hashlib.sha256(salt + password.encode()).hexdigest(), salt.hex()
        return hashlib.sha256(password.encode()).hexdigest()
    
    elif method == "bcrypt":
        # bcrypt.hashpw returns bytes; decode to string for storage
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
        return hashed.decode('utf-8')
    
    elif method == "argon2id":
        return def_hash.hash(password)
    
    else:
        return password

def verify_password(password, stored_hash, method, salt=None):
    if method == "sha256":
        if not salt:
            return hashlib.sha256(password.encode()).hexdigest() == stored_hash
        # Convert hex salt back to bytes
        salt_bytes = bytes.fromhex(salt)
        return hashlib.sha256(salt_bytes + password.encode()).hexdigest() == stored_hash
    
    elif method == "bcrypt":
        return bcrypt.checkpw(password.encode(), stored_hash.encode('utf-8')) 
    
    elif method == "argon2id":
        try:
            return def_hash.verify(stored_hash, password)
        except:
            return False
        
    else:
        return password == stored_hash
