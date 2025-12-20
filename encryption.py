from argon2 import PasswordHasher
import bcrypt, hashlib, os

def_hash = PasswordHasher(time_cost=1, memory_cost=65536, parallelism=1)


def hash_password(password, hash):

    if hash == "sha256":
        salt = os.urandom(16)
        return salt, hashlib.sha256(salt + password.encode()).hexdigest()
    
    elif hash == "bcrypt":
        return bcrypt.hashpw(password.encode() + bcrypt.gensalt(rounds=12))
    
    elif hash == "argon2id":
        return def_hash.hash(password)
    
    else:
        return password
        
    

def verify_password(password, stored_hash, hash, salt=None):
    if hash == "sha256":
        return hashlib.sha256(salt + password.encode()).hexdigest() == stored_hash
    
    elif hash == "bcrypt":
        return bcrypt.checkpw(password.encode(), stored_hash) 
    
    elif hash == "argno2id":
        try:
            def_hash.verify(password)
            return True
        except:
            return False
        
    else:
        return password == stored_hash
