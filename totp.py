import pyotp,time


#creating a secret token for user.
def creat_secret_token():
    return pyotp.random_base32()

#generating token based on the user's secret token.
def generate_token(secrec_token):
    totp = pyotp.TOTP(secrec_token)
    return totp.now()


#veryfying the token to mache the user.
def veryfy_totp(secret_token, totp_token):
    token = pyotp.TOTP(secret_token)
    return token.verify(totp_token)


#generating token based on the user's secret token with tome shiftting.
def generate_token_with_time_shift(totp_secret, time_shift):
    totp = pyotp.TOTP(totp_secret)
    current_time = int(time.time()) + time_shift 
    return totp.at(current_time)

#veryfying the secret_token to mache the token when the time is different.
def verify_totp_with_sync(secret, token, window=1):
    totp = pyotp.TOTP(secret) #Initialize a TOTP object using the shared secret

    now = time.time()

    #Iterate over adjacent TOTP time windows to tolerate clock shift
    for win in range(-window, window + 1):
        test_time = now + win * 30 #Simulate verification at a shifted time window (w * 30 seconds)
        if totp.verify(token, for_time=test_time):
            return True #Return True

    return False  
