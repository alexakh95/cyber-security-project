from app import app, db, User
import util
import multiprocessing
import time
from datetime import datetime
import csv
import requests
from app import init_db

LOGIN_URL = "http://127.0.0.1:5000/login"
USERS = util.get_usernames_by_category()
MAX_DURATION = 7200 #this is two hours 

def run_server():
    app.run(debug=False, use_reloader=False)
    
def password_spraying():
    
    with open("common_passwords.csv", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
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
                        if success :
                            break
                        if code_resp == 429:
                        
                            count+=1
                            if count == 30:
                                print("Attack has been blocked by the system")
                                return 
                            
                    else:
                        print(f"Time limit reached ({elapsed_time:.2f}s)Shutting down.")
                        return 
                    time.sleep(0.05) 
            

if __name__ == '__main__':

        # initiate the database with the configuration
        init_db()
        # Start server in a separate process
        server_process = multiprocessing.Process(target=run_server)
        server_process.start()
        
        # Wait a moment for the server to initialize
        time.sleep(2)
        try:
            # Run the attack script
            password_spraying()
            
        except Exception as e:
            print(f"An error occurred during spraying: {e}")
        
        # Terminate the server process to prepare for the next loop
        server_process.terminate()
        server_process.join()