from argon2 import PasswordHasher
import bcrypt, hashlib, os

#default parameters for Argon2id.
def_hash = PasswordHasher(time_cost=1, memory_cost=65536, parallelism=1)


#Creating hash by getting the password and hash type.
def hash_password(password, hash):

    if hash == "sha256":
        salt = os.urandom(16)
        return salt, hashlib.sha256(salt + password.encode()).hexdigest()
    
    elif hash == "bcrypt":
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
    
    elif hash == "argon2id":
        return def_hash.hash(password)
    #if no hash is defind.
    else:
        return password
        
    
#verufying the password with the stored hash, by hashing the password and compering with the stored one.
def verify_password(password, stored_hash, hash, salt=None):
    print("hash: ", stored_hash, password, hash)
    if hash == "sha256":
        return hashlib.sha256(salt + password.encode()).hexdigest() == stored_hash
    
    elif hash == "bcrypt":
        return bcrypt.checkpw(password.encode(), stored_hash) 
    
    elif hash == "argon2id":
        try:
            print("sldjjlfhdslhslhsjlfhls")
            def_hash.verify(stored_hash, password)
            return True
        except:
            return False
    #if no hash is defind.    
    else:
        return password == stored_hash
