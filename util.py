import json,yaml
from datetime import datetime

#open config file
with open("config.yaml", "r") as f:
    APP_CONFIG = yaml.safe_load(f)

GROUP_SEED = APP_CONFIG["GROUP_SEED"]
HASH_METHOD = APP_CONFIG["config"]["hash"]
SALT = APP_CONFIG["config"]["salt"]
PEPPER = APP_CONFIG["config"]["pepper"]
PROTECTION = APP_CONFIG["protection"]
ATTACK = APP_CONFIG["attack"]


def users_pass_list():
    with open("json/user.json", "r") as f:
        data = json.load(f)
    
    users = []

    for catigory, user_list in data.items():
        for user in user_list:
            users.append(
                 (user['username'],
                 user['password'])
            )

    return users

def users_list():
    with open("json/user.json", "r") as f:
        data = json.load(f)
    
    users = []

    for catigory, user_list in data.items():
        for user in user_list:
            users.append(
                user['username']
            )

    return users

def log_security_event(username,result,latency_ms):
    filename = f"json_logs/logs_{HASH_METHOD}_{PROTECTION}_{ATTACK}.json"
    
    log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "username": username,
            "result":result,
            "latency_ms": latency_ms,
            "hash_mode": HASH_METHOD,
            "prot_flag": PROTECTION,
            "group_seed": GROUP_SEED
        }
    
    with open(filename, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
       