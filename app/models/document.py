from datetime import datetime
from app import db

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_hash = db.Column(db.String(64), index=True)  # For quick duplicate checking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    scans_as_source = db.relationship('Scan', 
                                    foreign_keys='Scan.source_document_id',
                                    backref='source_document',
                                    lazy='dynamic')
    scans_as_match = db.relationship('Scan',
                                   foreign_keys='Scan.matched_document_id',
                                   backref='matched_document',
                                   lazy='dynamic')

    def __repr__(self):
        return f'<Document {self.filename}>'

class Scan(db.Model):
    __tablename__ = 'scans'

    id = db.Column(db.Integer, primary_key=True)
    source_document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    similarity_score = db.Column(db.Float)
    matched_document_id = db.Column(db.Integer, db.ForeignKey('documents.id'))

    def __repr__(self):
        return f'<Scan {self.id} by User {self.user_id}>' 