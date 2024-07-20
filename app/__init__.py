from flask import Flask
from app.config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Import routes after initializing app to avoid circular imports
from app import routes
