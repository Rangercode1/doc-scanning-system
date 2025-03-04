from app import create_app, db
from app.models.user import User

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True,
                credits=999999  # Unlimited credits for admin
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully!')
            print('Username: admin')
            print('Password: admin123')
            print('IMPORTANT: Change these credentials in production!')
        else:
            print('Admin user already exists.')

if __name__ == '__main__':
    init_db() 