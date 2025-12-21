import json


def users_pass_list():
    with open("json/user.json", "r") as f:
        data = json.load(f)
    
    users = []

    for catigory, user_list in data.items():
        for user in user_list:
            users.append({
                "username": user['username'],
                "password": user['password']
            })

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


def log_attempt(data,log_file=""):
    with open(log_file, "a", encoding="utf-8") as f:
        json.dump(data, f)
        f.write("\n")         