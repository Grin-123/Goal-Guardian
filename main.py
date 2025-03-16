from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from models.user import User, db
from models.transaction import Transaction, BudgetCategory
import os

name = "Goal Guardian"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
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

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(5)
    categories = BudgetCategory.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', transactions=transactions, categories=categories)

@app.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        transaction = Transaction(
            amount=float(request.form['amount']),
            description=request.form['description'],
            category=request.form['category'],
            transaction_type=request.form['type'],
            user_id=current_user.id
        )
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('dashboard'))
    categories = BudgetCategory.query.filter_by(user_id=current_user.id).all()
    return render_template('add_transaction.html', categories=categories)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)