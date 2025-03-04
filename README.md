# Document Scanning and Matching System

A self-contained document scanning and matching system with a built-in credit system. Users can scan and compare documents, with each user getting 20 free scans per day.

## Features

- User Authentication & Role Management
- Credit System with Daily Free Credits
- Document Upload & Text Matching
- Smart Analytics Dashboard
- AI-Powered Document Matching (Optional)

## Tech Stack

- Backend: Python (Flask)
- Database: SQLite
- Frontend: HTML, CSS, JavaScript
- Authentication: Flask-Login
- Text Matching: Custom algorithm + Optional AI integration

## Project Structure

```
.
├── app/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── models/
│   ├── routes/
│   └── utils/
├── instance/
├── tests/
├── .env
├── .gitignore
├── config.py
├── requirements.txt
└── run.py
```

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   ```

4. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Run the application:
   ```bash
   flask run
   ```

## API Endpoints

- POST `/auth/register` - User registration
- POST `/auth/login` - User login
- GET `/user/profile` - Get user profile & credits
- POST `/scan` - Upload document for scanning
- GET `/matches/<doc_id>` - Get matching documents
- POST `/credits/request` - Request additional credits
- GET `/admin/analytics` - Get analytics (admin only)

## Credit System

- 20 free scans per day (resets at midnight)
- Request additional credits from admin
- Each scan costs 1 credit
- Admin can approve/deny credit requests

## Security Features

- Password hashing using bcrypt
- Session-based authentication
- CSRF protection
- Secure file handling

## Testing

Run tests using:
```bash
python -m pytest
```

## License

MIT License 