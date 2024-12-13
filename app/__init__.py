from flask import Flask  # Import Flask for creating the app
from flask_sqlalchemy import SQLAlchemy  # Import SQLAlchemy for database management

# Initialize the SQLAlchemy object (database)
db = SQLAlchemy()

# Function to create and configure the Flask application
def create_app():
    """
    This function initializes and configures the Flask application.
    It also sets up the database and registers blueprints for routing.
    """
    app = Flask(__name__)  # Create a Flask application instance
    
    # Load configuration settings from the Config class in the 'config' module
    app.config.from_object('config.Config')

    # Initialize the database with the app
    db.init_app(app)

    # Import and register blueprints for different routes/modules
    from app.routes import upload_routes, file_routes
    app.register_blueprint(upload_routes.bp)  # Register routes for file uploads
    app.register_blueprint(file_routes.bp)  # Register routes for file management

    # Register the blueprint for text processing with a URL prefix
    from app.routes.text_routes import bp as text_bp
    app.register_blueprint(text_bp, url_prefix='/text')

    # Register the blueprint for image processing with a URL prefix
    from app.routes.image_routes import bp as image_bp
    app.register_blueprint(image_bp, url_prefix='/images')

    # Ensure all database tables are created if they do not exist
    with app.app_context():
        db.create_all()  # Create database tables based on defined models

    # Return the configured Flask application instance
    return app
