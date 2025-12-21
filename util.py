import itertools, string, random, json


MAX_PASS = 300000


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


def users_list(category):
    with open("json/user.json", "r") as f:
        data = json.load(f)
    
    users = []

    if category in data:
        print(category)
        for user in data[category]:
            users.append(
                user['username']
            )
    return users


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


def rand_generate_sequences(file):
    length = random.choice([8, 9])

    characters = string.ascii_letters + string.digits

    with open(file, "w") as f:
        for i in range(100000):
            random_text = ''.join(random.choice(characters) for _ in range(length))
            f.write(random_text + '\n')


def generate_sequences(type, file, name=None, min_len=None):
    if type == "mudium":
        med_generate_sequences(file, name, min_len)
    else:
        rand_generate_sequences(file)
       