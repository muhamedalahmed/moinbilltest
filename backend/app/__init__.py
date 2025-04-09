import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus .env-Datei
load_dotenv()

# Initialisiere Flask-Erweiterungen
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def create_app(config_class=None):
    """
    Erstellt und konfiguriert die Flask-Anwendung
    """
    app = Flask(__name__)
    
    # Konfiguration aus Umgebungsvariablen
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///buchhaltung.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-key-change-in-production')
    
    # E-Mail-Konfiguration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Initialisiere Erweiterungen mit der App
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    # Registriere Blueprints
    from app.api import customers_bp, invoices_bp, items_bp, recurring_invoices_bp, payments_bp, email_templates_bp, users_bp
    app.register_blueprint(customers_bp, url_prefix='/api/customers')
    app.register_blueprint(invoices_bp, url_prefix='/api/invoices')
    app.register_blueprint(items_bp, url_prefix='/api/items')
    app.register_blueprint(recurring_invoices_bp, url_prefix='/api/recurring-invoices')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(email_templates_bp, url_prefix='/api/email-templates')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    # Erstelle Datenbanktabellen
    with app.app_context():
        db.create_all()
    
    return app
