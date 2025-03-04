from app import create_app
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

app = create_app()
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Vercel serverless function handler
def handler(request):
    """Handle incoming HTTP requests in Vercel's serverless environment."""
    if request.method == 'POST':
        return app(request.environ, lambda x, y: y)(request.data)
    return app(request.environ, lambda x, y: y)('') 