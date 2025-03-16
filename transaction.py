from datetime import datetime
from . import db

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'expense' or 'income'
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Transaction {self.description}: {self.amount}>'

class BudgetCategory(db.Model):
    __tablename__ = 'budget_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    monthly_limit = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<BudgetCategory {self.name}: {self.monthly_limit}>'