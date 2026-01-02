import itertools, string, random, json, yaml
from datetime import datetime

#open config file
with open("config.yaml", "r") as f:
    APP_CONFIG = yaml.safe_load(f)

GROUP_SEED = APP_CONFIG["GROUP_SEED"]
HASH_METHOD = APP_CONFIG["config"]["hash"]
SALT = APP_CONFIG["config"]["salt"]
PEPPER = APP_CONFIG["config"]["pepper"]

PROTECTION = APP_CONFIG["protection"]
if PROTECTION is None:
    PROTECTION = ""
ATTACK = APP_CONFIG["attack"]

MAX_PASS = 100000

#getting from json file the user's name and password.
def users_pass_list():
    """
    Returns a list of tuples (usernames,password). 
    """
    with open("json/user.json", "r") as f:
        data = json.load(f)
    
    users = []

    for _, user_list in data.items():
        for user in user_list:
            user_entry = (
                 user['username'],
                 user['password'],
            )
            users.append(user_entry)
    return users

#getting the user's totp secret key if the is.
def get_secret_key(username, category):
    with open("json/user.json", "r") as f:
        data = json.load(f)

    users = data[category]

    for user in users:
        if user['username'] == username:
            return user['totp_secret'] if 'totp_secret' in user else None 
    

#getting list of users from json file base on the strength of the passwords.
def get_usernames_by_category(category=None):
    """
    Returns a list of usernames. 
    If category is provided ('weak', 'medium', 'strong'), returns users in that group.
    If category is None, returns all usernames from all groups.
    """
    with open("json/user.json", "r") as f:
        data = json.load(f)
        
    if category:
        # Get users from the specific key, default to empty list if category doesn't exist
        users = data.get(category, [])
        return [user["username"] for user in users]
    
    # If no category, flatten all lists and extract usernames
    all_usernames = []
    for cat_list in data.values():
        all_usernames.extend([user["username"] for user in cat_list])
    
    return all_usernames

#creting a passowrd list base on the name of the user.
def med_generate_sequences(file, name, min_length=4, max_length=6):
    name_lower = name.lower()
    count = 0 
    print(name_lower)
    substring = [name_lower[:i] for i in range(1, len(name_lower) + 1)]
    numbers = '0123456789'
    with open(file, "w") as f:
        for sub in substring:
            sub_len = len(sub)
            for leng in range(min_length, max_length + 1):
                if count > MAX_PASS:
                    break
                num_digits = leng - sub_len
                if num_digits > 0:
                    for num_combo in itertools.product(numbers, repeat=num_digits):
                        num_str = ''.join(num_combo)
                        f.write(sub + num_str + '\n')
                        f.write(num_str + sub + '\n')
                        count += 2
                else:
                    f.write(sub + '\n')
                    count += 1

#creating a strong password's list. 
def rand_generate_sequences(file):
    length = random.choice([8, 9])

    characters = string.ascii_letters + string.digits

    with open(file, "w") as f:
        for i in range(MAX_PASS):
            random_text = ''.join(random.choice(characters) for _ in range(length))
            f.write(random_text + '\n')


def generate_sequences(type, file, name=None, min_len=None):
    if type == "mudium":
        med_generate_sequences(file, name, min_len)
    else:
        rand_generate_sequences(file)


def log_security_event(username,result,latency_ms):


    for key, val in PROTECTION.items():
        if val :
            protect_type = key
        else:
            protect_type= ""
            break
    
    for key, val in ATTACK.items():
        if val :
            attack_type = key
    
    filename = f"json_logs/logs_{HASH_METHOD}_{protect_type}_{attack_type}.json"
    
    log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "username": username,
            "result":result,
            "latency_ms": latency_ms,
            "hash_mode": HASH_METHOD,
            "prot_flag": protect_type,
            "group_seed": GROUP_SEED
        }
    
    with open(filename, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
       