from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from models import db, User, Transaction, Notification
from services.email_service import EmailService
import schedule
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        bank_name = request.form['bank_name']
        email_password = request.form['email_password']
        
        user = User(username=username, email=email, bank_name=bank_name)
        user.set_password(password)
        user.email_password = email_password  # In production, encrypt this!
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Budget management routes
@app.route('/dashboard')
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc()).limit(10).all()
    remaining_budget = current_user.get_remaining_budget()
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        read_at=None
    ).all()
    return render_template('dashboard.html',
                         transactions=transactions,
                         remaining_budget=remaining_budget,
                         notifications=notifications)

@app.route('/set_budget', methods=['POST'])
@login_required
def set_budget():
    amount = float(request.form['amount'])
    duration_days = int(request.form['duration'])
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=duration_days)
    
    current_user.set_budget(amount, start_date, end_date)
    db.session.commit()
    
    flash('Budget has been set successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/fetch_transactions')
@login_required
def fetch_transactions():
    """Manually trigger email fetching"""
    process_emails(current_user.id)
    return redirect(url_for('dashboard'))

def process_emails(user_id):
    """Process emails for a user and update transactions"""
    user = User.query.get(user_id)
    if not user:
        return
    
    email_service = EmailService(user.email, user.email_password, user.bank_name)
    if not email_service.connect():
        return
    
    try:
        transactions = email_service.fetch_transaction_emails()
        for t in transactions:
            # Check if transaction already exists
            exists = Transaction.query.filter_by(
                user_id=user.id,
                date=t['date'],
                amount=t['amount'],
                description=t['description']
            ).first()
            
            if not exists:
                transaction = Transaction(
                    user_id=user.id,
                    date=t['date'],
                    amount=t['amount'],
                    description=t['description'],
                    type=t['type']
                )
                db.session.add(transaction)
        
        db.session.commit()
        
        # Check budget status and create notification if needed
        if user.should_notify():
            notification = Notification(
                user_id=user.id,
                type='budget_warning',
                message=f'You have used {user.get_remaining_budget():.2f} of your budget!'
            )
            db.session.add(notification)
            db.session.commit()
            
    finally:
        email_service.disconnect()

def schedule_email_processing():
    """Schedule regular email processing"""
    while True:
        with app.app_context():
            users = User.query.all()
            for user in users:
                process_emails(user.id)
        time.sleep(3600)  # Run every hour

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Start email processing in background
    email_thread = threading.Thread(target=schedule_email_processing)
    email_thread.daemon = True
    email_thread.start()
    
    app.run(debug=True) 