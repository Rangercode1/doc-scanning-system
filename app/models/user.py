from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    credits = db.Column(db.Integer, default=20)
    last_credit_reset = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_oauth_user = db.Column(db.Boolean, default=False)
    
    # Relationships with dynamic loading to enable query operations
    documents = db.relationship('Document', backref=db.backref('owner', lazy=True), lazy='dynamic')
    scans = db.relationship('Scan', backref=db.backref('user', lazy=True), lazy='dynamic')
    # Credit requests relationships are defined in CreditRequest model

    def set_password(self, password):
        if password:
            self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        if not self.password_hash or self.is_oauth_user:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)

    def reset_daily_credits(self):
        """Reset credits to daily limit if last reset was before today"""
        today = datetime.utcnow().date()
        if self.last_credit_reset.date() < today:
            self.credits = 20
            self.last_credit_reset = datetime.utcnow()
            db.session.commit()

    def deduct_credit(self):
        """Deduct one credit and return True if successful"""
        if self.credits > 0:
            self.credits -= 1
            db.session.commit()
            return True
        return False

    def add_credits(self, amount):
        """Add credits to user's balance"""
        self.credits += amount
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>' 