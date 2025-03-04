from datetime import datetime
from app import db

class CreditRequest(db.Model):
    __tablename__ = 'credit_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    processed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Define relationships
    user = db.relationship(
        'User',
        foreign_keys=[user_id],
        backref=db.backref('user_credit_requests', lazy=True)
    )
    processed_by = db.relationship(
        'User',
        foreign_keys=[processed_by_id],
        backref=db.backref('processed_credit_requests', lazy=True)
    )

    def __repr__(self):
        return f'<CreditRequest {self.id} by User {self.user_id}>' 