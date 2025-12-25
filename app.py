from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import encryption, protection
import yaml, util
import time
from datetime import datetime, timedelta

#open config file
with open("config.yaml", "r") as f:
    APP_CONFIG = yaml.safe_load(f)

#initialize the web server with the config file
HASH_METHOD = APP_CONFIG["config"]["hash"]
SALT = APP_CONFIG["config"]["salt"]
PEPPER = APP_CONFIG["config"]["pepper"]
PROTECTION = APP_CONFIG["protection"]

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
    locked_until = db.Column(db.DateTime, nullable=True)
        
    salt = db.Column(db.String(256), nullable=True)
     
    def set_password(self, password):
        if SALT:
            self.password, self.salt = encryption.hash_password(password, method=HASH_METHOD,use_salt=SALT)
        else:
            self.password = encryption.hash_password(password,method=HASH_METHOD)

    def check_password(self, password):
        return encryption.verify_password(password, self.password, method= HASH_METHOD)

    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        new_user = User(username=username)
        new_user.set_password(password, method=HASH_METHOD)

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
            if not protection.check_rate_limit(ip):
                util.log_security_event(username=username,result='fail',latency_ms= (time.perf_counter() - start) * 1000)
                flash("Too many attempts, please wait.")
                return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        #TOTP protection that comes after successful password verification
        if user and user.check_password(request.form.get('password')):
            if PROTECTION["TOTP"]:
                flash("TOTP required (not implemented)")
                return render_template('login.html')
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
        
    return render_template('login.html')




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
        

if __name__ == '__main__':
    app.run(debug=True)