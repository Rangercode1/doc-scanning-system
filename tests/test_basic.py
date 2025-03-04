import unittest
from app import create_app, db
from app.models.user import User
from app.models.document import Document, Scan, CreditRequest
from config import Config
import os
import tempfile

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    WTF_CSRF_ENABLED = False

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Create test user
        self.test_user = User(username='testuser', email='test@example.com')
        self.test_user.set_password('password123')
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)

    def test_login_logout(self):
        # Test login
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Test logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_credit_system(self):
        # Login
        self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Check initial credits
        self.assertEqual(self.test_user.credits, 20)
        
        # Test credit deduction
        self.assertTrue(self.test_user.deduct_credit())
        self.assertEqual(self.test_user.credits, 19)
        
        # Test credit reset
        self.test_user.credits = 0
        db.session.commit()
        self.test_user.reset_daily_credits()
        self.assertEqual(self.test_user.credits, 20)

    def test_document_upload(self):
        # Login
        self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.txt') as temp:
            temp.write(b'Test document content')
            temp.seek(0)
            
            response = self.client.post('/upload', data={
                'file': (temp, 'test.txt')
            }, follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            document = Document.query.filter_by(filename='test.txt').first()
            self.assertIsNotNone(document)
            self.assertEqual(document.user_id, self.test_user.id)

    def test_document_matching(self):
        # Create two similar documents
        doc1 = Document(
            filename='doc1.txt',
            content='This is a test document about Python programming',
            user_id=self.test_user.id
        )
        doc2 = Document(
            filename='doc2.txt',
            content='This is another document about Python programming',
            user_id=self.test_user.id
        )
        db.session.add_all([doc1, doc2])
        db.session.commit()
        
        # Test similarity calculation
        from app.utils.document_matching import basic_text_similarity
        similarity = basic_text_similarity(doc1.content, doc2.content)
        self.assertGreater(similarity, 0.5)

if __name__ == '__main__':
    unittest.main() 