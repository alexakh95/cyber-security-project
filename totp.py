import pyotp,time



#creating a secret token for user.
def creat_secret_token():
    return pyotp.random_base32()


#veryfying the token to mache the user.
def veryfy_totp(username, totp_token):
    token = pyotp.TOTP("user_token")
    return token.verify(totp_token)

#generating token based on the user's secret token.
def generate_token(username):
    totp = pyotp.TOTP("get the user's secret token")
    return totp.now()

#generating token based on the user's secret token with tome shiftting.
def generate_token_with_time_shift(totp_secret, time_shift):
    totp = pyotp.TOTP(totp_secret)
    current_time = int(time.time()) + time_shift 
    return  totp.at(current_time)


#veryfying the secret_token to mache the token when the time is different.
def verify_totp_with_sync(secret, token, window=1):
    totp = pyotp.TOTP(secret) #Initialize a TOTP object using the shared secret
    now = time.time()

    #Iterate over adjacent TOTP time windows to tolerate clock shift
    for win in range(-window, window + 1):
        test_time = now + win * 30 #Simulate verification at a shifted time window (w * 30 seconds)
        if totp.verify(token, for_time=test_time):
            return True, win * 30  #Return True along with the applied time correction (in seconds)

    return False, None    


#testing to see the sync of the server.
shift = 47 
secret = creat_secret_token()
token = generate_token_with_time_shift(secret, shift)

ok, correction = verify_totp_with_sync(secret, token)

print({
    "imposed_drift_sec": shift,
    "corrected_drift_sec": correction,
    "final_error_sec": shift - correction if ok else None,
    "success": ok
})