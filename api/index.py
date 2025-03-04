from app import create_app

app = create_app()

# Vercel serverless function handler
def handler(request):
    return app(request) 