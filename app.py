from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import encryption, protection
import yaml, util
import time
import secrets
from datetime import datetime, timedelta
approved_captcha_tokens = {}

#open config file
with open("config.yaml", "r") as f:
    APP_CONFIG = yaml.safe_load(f)

#initialize the web server with the config file


GROUP_SEED = APP_CONFIG["GROUP_SEED"]
PROTECTION = APP_CONFIG["protection"]
MAX_ATTEMPTS = 10

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(256), nullable=False)
    
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked = db.Column(db.Boolean, default=False)
        
    salt = db.Column(db.String(256), nullable=True)
     
    def set_password(self, password):
        self.password, self.salt = encryption.hash_password(password)
        
    def check_password(self, password):
        return encryption.verify_password(password, self.password,self.salt)

    def is_locked(self, lock):
        self.locked = lock
    
    def update_failed_attempts(self):
        self.failed_login_attempts = self.failed_login_attempts+1
        


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login_totp', methods=['GET', 'POST'])
def login_totp():
    if request.method == 'POST':
        username = session.get('username')

        #Check if the TOTP token is valid
        result = totp.veryfy_totp(session.get('totp_secret'), request.form.get('TOTP_token'))
        
        latency = (time.perf_counter() - session.get('start')) * 1000

        if result:
            util.log_security_event(username=username, result='totp_success', latency_ms=latency)
            return redirect(url_for('dashboard')), 200
        
        util.log_security_event(username=username,result='totp_fail',latency_ms= latency)
        flash('Invalid credentials')

    return render_template('login.html'), 501


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        ip = request.remote_addr
        start = time.perf_counter()
        
        #rate limit-protection
        if PROTECTION["rate-limit"]:
            if not protection.check_rate_limit(username):
                util.log_security_event(username=username,result='blocked',latency_ms= (time.perf_counter() - start) * 1000)
                flash("Too many attempts, please wait.")
                return render_template('login.html'), 429 
        
        user = User.query.filter_by(username=username).first()
        
        #TOTP protection that comes after successful password verification
        if user and user.check_password(request.form.get('password')):
            if PROTECTION["lockout"] and not user.locked:
                user.failed_login_attempts = 0
                db.session.commit()
            if PROTECTION["TOTP"]:
                flash("TOTP required (not implemented)")
                return render_template('login.html')
            # CALCULATE LATENCY FOR SUCCESS
            latency = (time.perf_counter() - start) * 1000
            
            # --- SUCCESS LOGGING ---
            util.log_security_event(username=username, result='success', latency_ms=latency)
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
        
        # 4. FAILURE PATH
        if PROTECTION["lockout"]:
            if user.failed_login_attempts >= MAX_ATTEMPTS:
                user.is_locked(True)
                db.session.commit()
                latency = (time.perf_counter() - start) * 1000
                util.log_security_event(username=username, result='locked', latency_ms=latency)
                return render_template('login.html'), 429 
            else:
                user.update_failed_attempts()
            
            db.session.commit()
               
        latency = (time.perf_counter() - start) * 1000
        util.log_security_event(username=username, result='fail', latency_ms=latency)
        flash('Invalid credentials')
        
    return render_template('login.html')


@app.route('/admin/get_captcha_token')
def get_simulation_token():
    seed = request.args.get('group_seed')
    user_id = request.args.get('user_id')
    
    if seed != GROUP_SEED:
        return {"error": "Unauthorized"}, 401

    
    sim_token = secrets.token_hex(16)
    approved_captcha_tokens[user_id] = sim_token
    
    return {"captcha_token": sim_token}

@app.route('/dashboard')
@login_required
def dashboard():
    return f"Hello, {current_user.username}! This is a protected page."

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def init_db():
    with app.app_context():
        db.drop_all() # Clear previous data
        db.create_all()  # Creates the .db file and tables
        
        user_list = util.users_pass_list()
        for username, password in user_list:
            new_user = User(username=username)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
        

