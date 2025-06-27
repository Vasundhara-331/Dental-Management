# This file marks the app directory as a Python package.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql://dental_user:dental_pass@localhost:3306/dental_management')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)
    socketio.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.appointments import appointments_bp
    from app.routes.doctors import doctors_bp
    from app.routes.patients import patients_bp
    from app.routes.chatbot import chatbot_bp
    from app.routes.queue import queue_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(appointments_bp, url_prefix='/api/appointments')
    app.register_blueprint(doctors_bp, url_prefix='/api/doctors')
    app.register_blueprint(patients_bp, url_prefix='/api/patients')
    app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
    app.register_blueprint(queue_bp, url_prefix='/api/queue')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
