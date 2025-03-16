from datetime import datetime
from werkzeug.security import generate_password_hash
from flask_login import UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    bank_name = db.Column(db.String(100), nullable=True)
    email_password = db.Column(db.String(255), nullable=True)  # Store securely in production!

    @classmethod
    def create_user(cls, username, email, password, bank_name=None, email_password=None):
        """
        Creates a new user instance with optional bank details.
        
        Args:
            username: User's username
            email: User's email
            password: User's password
            bank_name: Name of user's bank for email filtering
            email_password: Password for email access (store securely in production!)
        """
        user = cls(
            username=username,
            email=email,
            bank_name=bank_name,
            email_password=email_password
        )
        user.set_password(password)
        return user

    @classmethod
    def get_user(cls, username):
        return User.query.filter_by(username=username).first()
    
    @classmethod
    def get_total_expenses(cls, month=None):
        """Returns the total expenses for a given time"""
        from models.transaction import Transaction  # Import here to avoid circular imports
        query = Transaction.query.filter_by(user_id=current_user.id)
        if month:
            query = query.filter(Transaction.date.month == month)
        return query.sum(Transaction.amount)

    def get_budget_status(self):
        from models.transaction import Transaction  # Import here to avoid circular imports
        query = Transaction.query.filter_by(user_id=self.id)
        total_spent = query.sum(Transaction.amount) or 0
        return total_spent

    transactions = db.relationship('Transaction', backref='user')
    budgets = db.relationship('Budget', backref='user')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def __repr__(self):
        return f'<User {self.username}'

    def update_bank_details(self, bank_name, email_password):
        """Update user's bank details for email filtering"""
        self.bank_name = bank_name
        self.email_password = email_password  # Store securely in production!
        return True

        