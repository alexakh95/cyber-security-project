import multiprocessing
import time
import yaml
from server.server import app, init_db
from attacks import ps, bruteforce

#open config file
with open("config.yaml", "r") as f:
    APP_CONFIG = yaml.safe_load(f)

ATTACK_TYPE = APP_CONFIG['attack']

def run_server():
    app.run(debug=False, use_reloader=False)

if __name__ == '__main__':

        # initiate the database with the configuration
        init_db()
        
        # Start server in a separate process
        server_process = multiprocessing.Process(target=run_server)
        server_process.start()
        
        # Wait a moment for the server to initialize
        time.sleep(2)
        try:
            for item in ATTACK_TYPE:
                if item == "bruteforce" and ATTACK_TYPE[item]:
                   bruteforce.brute_rorce()
                if item == "passwordspraying" and ATTACK_TYPE[item]:
                    ps.password_spraying()
            
        except Exception as e:
            print(f"An error occurred during spraying: {e}")
        
        # Terminate the server process to prepare for the next loop
        server_process.terminate()
        server_process.join()