# app.py
from flask import Flask
from flask_cors import CORS
from routes.chat_routes import chat_bp
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)

app.register_blueprint(chat_bp)

if __name__ == '__main__':
    app.run(debug=True)