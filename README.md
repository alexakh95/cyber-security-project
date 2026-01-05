# "A Comparative Analysis of Password-Based Authentication Mechanisms”

## Primary Goal
To conduct a reproducible experimental study comparing password hashing and authentication
mechanisms (e.g., bcrypt, Argon2, SHA-256 + salt), examining the impact of various security
protection mechanisms such as salt, pepper, rate limiting, account lockout, CAPTCHA, and TOTP,
and to perform a statistical analysis of the collected data.

## Secondary Goal
1.Measure success rates and time-to-compromise under a variety of protection mechanisms.
2.Quantify the effect of each protection mechanism individually and in combination.
3.Evaluate the usability–security trade-off and system performance for each approach.
4.Analyze and compare the experimental result

## Tech Stack
Language: Python 
Framework: Flask 
Database: SQLite 

## Architecture
The system is designed as a configurable authentication server that enables controlled experimentation with different password hashing algorithms and defensive mechanisms under simulated attack scenarios.

## High-Level Design 
The arcitecture consists of three main components:
1. Authentication server
2. Configuration Layer
3. Attack simulation Module

1. **Authentication server**  
The server is responsible for: managing user registration and authentication,
securely storing usernames and password hashes,enforcing curity and protection mechanism 
during authentication.
Core responsibilities: 
- password hashing using configurable algorithms (e.g. bcrypt, sha256, argnoid2) + using salt, pepper
- authentication requests handling (login attemps)
- Tracking authentication state (number of failed login attempts, lockout status etc.)

2. **Configuration Layer** 
Security mechanisms are fully configurable via a configuration file, allowing reproducible experiments.

The configuration defines:
- Password hashin algorithms and parameters
- Enable protection mechanism, such as rate-limit, lockout, TOTP, CAPTCHA , Salt and Pepper usage.

3. **Attack simulation model**
To evaluate the effectiveness of authentication defenses, the system includes controlled attack simulations:
- Password spraying attacks
- Brute-force attacks
These attacks are executed against the authentication server while varying: hashing algorithms, protection mechanisms,defense combinations
The module records metrics such as:
- Attack success rate
- Time-to-compromise
- Number of authentication attempts
- Triggered defense events (e.g., CAPTCHA, lockout)

**Data Flow Overview**
1. An authentication request is sent to the server.
2. The server validates credentials using the configured hashing algorithm.
3. Protection mechanisms are applied based on configuration.
4. Attack attempts are logged and metrics are collected.
5. Results are stored for statistical analysis.

## Project Structure
```bash
├── attacks
│   └── ps.py
│   └── bruteforce.py
├── bf_passwords
│   └── weakpass.txt
├── common_passwords.csv
├── config.yaml
├── experiment
│   └── run_experiment.py
├── instance
│   └── db.sqlite
├── json_logs
│   
├── README.md
├── server
│   ├── encryption.py
│   ├── protection.py
│   ├── server.py
│   ├── templates
│   │   ├── login.html
│   │   └── register.html
│   ├── totp.py
│   └── util.py
└── users
    └── user.json
```

## Installation
Prerequirments: Python >= 3.x ,pip

### Steps
```bash
git clone https://github.com/alexakh95/cyber-security-project
cd cyber-security-project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt 
```

## Running an Experiment
1. **Configure** the `config.yaml` file by selecting the attack type, protection mechanisms, and hash function.
This example demonstrates running a **password spraying attack** with server-side protections enabled, including **account lockout**, salt and pepper, and the **SHA-256** hashing algorithm.
For brute-force attacks, it is possible to select the target users based on their password strength (weak, medium, or strong).

### Example configuration:

```yaml
attack:
  bruteforce: false
  passwordspraying: true

config:
  hash: "sha256"
  pass_level:
  salt: true
  pepper: true

protection:
  captcha: false
  lockout: true
  rate-limit: false
  TOTP: false

GROUP_SEED: 114467408
```

2. **Run the experiment**:
 
```bash
python -m experiment.run_experiment
```