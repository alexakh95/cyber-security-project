GROUP_SEED = 313131

from flask import Flask, request, jsonify
from dbhandler import create_db, get_data, stor_data
from encryption import hash_password, verify_password
from util import *
import sqlite3, json, time


app = Flask(__name__)

HASH = ""

def register_user(username, password):
    salt = None
    if HASH == "sha256":
        salt, hashed = hash_password(password, HASH)
    else:
        hashed = hash_password(password, HASH)
    stor_data(username, hashed, salt)


def init_register():
    create_db()
    users = users_pass_list()
    for iterm in users:
        username = iterm['username']
        password = iterm['password']
        register_user(username, password)

init_register()

            
@app.route('/')
def home():
    return "Welcom."


@app.route('/register', methods=["POST"])
def register():
    username = request.json.get("username")
    password = request.json.get("password")

    return jsonify({"register": "succesed"}), 200
    



@app.route('/login', methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) #Time stamp.
    start = time.perf_counter() #Starting clock for latency.

    hashed, salt = get_data(username)
    if not hashed:
        latency_ms = (time.perf_counter() - start) * 1000
        log(timestamp, username, HASH, None, "fail", latency_ms)
        return jsonify({"status": "incorect user name"}), 401
    
    result = verify_password(password, hashed, HASH, salt)
    latency_ms = (time.perf_counter() - start) * 1000

    if result:
        log(timestamp, username, HASH, None, "success", latency_ms)
        return jsonify({"status": "success"}), 200
    else:
        log(timestamp, username, HASH, None, "fail", latency_ms)
        return jsonify({"status": "failure"}), 401
    

 
def log(timestamp, usernmae, hash, protections, result, latency):

    LOG_FILE = "json/attempts.log"
    attempt = {
            "timestamp": timestamp,
            "group_seed": GROUP_SEED,
            "usermane": usernmae,
            "hash_mode": hash,
            "protection_flags": protections,
            "result": result,
            "latency_ms": latency
        }

    with open(LOG_FILE, "a") as log:
        log.write(json.dumps(attempt) + "\n")



if __name__ == "__main__":
    app.run()
    




