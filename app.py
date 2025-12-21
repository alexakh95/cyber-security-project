from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import encryption
from collections import defaultdict
import yaml
from datetime import datetime, timedelta

#open config file
with open("config.yaml", "r") as f:
    APP_CONFIG = yaml.safe_load(f)

#initialize the web server with the config file
HASH_METHOD = APP_CONFIG["config"]["hash"]
SALT = APP_CONFIG["config"]["salt"]
PEPPER = APP_CONFIG["config"]["pepper"]
PROTECTION = APP_CONFIG["protection"]

login_attempts = defaultdict(list)

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
    if SALT:
        salt = db.Column(db.String(256), nullable=True)
     
    def set_password(self, password,method = ""):
        self.password = encryption.hash_password(password, method=method)

    def check_password(self, password,method = ""):
        return encryption.verify_password(password, self.password, method= method)



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

        #rate limit-protection
        if PROTECTION["rate-limit"]:
            now = datetime.utcnow()
            login_attempts [ip] = [
                t for t in login_attempts[ip]
                if now - t < timedelta(seconds=60)
            ]

            if len(login_attempts[ip]) >= 10:
                flash("Too many attempts, slow down")
                return render_template('login.html')

            login_attempts[ip].append(now)
        
        user = User.query.filter_by(username=request.form.get('username')).first()
        
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

if __name__ == '__main__':
    app.run(debug=True)