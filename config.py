import os  # Import the os module for handling file paths

# Configuration class for the Flask application
class Config:
    """
    This class contains configuration settings for the Flask application.
    It includes database configuration, file upload paths, and other app-specific settings.
    """
    
    # Database connection string for SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456789@localhost/Corporatica'
    """
    SQLALCHEMY_DATABASE_URI:
    - Specifies the URI for connecting to a PostgreSQL database.
    - Format: 'postgresql://<username>:<password>@<host>/<database_name>'
    - In this case:
        - Username: postgres
        - Password: 123456789
        - Host: localhost (running locally)
        - Database: Corporatica
    """

    # Disable SQLAlchemy modification tracking to reduce overhead
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """
    SQLALCHEMY_TRACK_MODIFICATIONS:
    - Set to False to disable SQLAlchemy's event system that tracks object modifications.
    - This improves performance and avoids unnecessary warnings.
    """

    # Define the base directory of the application
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    """
    BASE_DIR:
    - Provides the absolute path to the directory containing this configuration file.
    - Useful for creating paths relative to the application's root directory.
    """

    # Define the directory where uploaded files will be stored
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'files')
    """
    UPLOAD_FOLDER:
    - Specifies the path where uploaded files will be saved.
    - Combines BASE_DIR with the 'files' folder.
    - Ensures all uploads are organized under a specific folder in the application directory.
    """
