from app import db  # Import the SQLAlchemy object from the app module
from datetime import datetime  # Import datetime for timestamping

# Define a database model for uploaded files
class UploadedFile(db.Model):
    """
    This model represents the uploaded files stored in the database.
    Each file has an ID, filename, file path, and a timestamp for when it was uploaded.
    """

    __tablename__ = 'uploaded_files'  # Specify the table name in the database

    # Define the primary key column for the table
    id = db.Column(db.Integer, primary_key=True)
    """
    id: A unique identifier for each uploaded file.
    - Type: Integer
    - Primary Key: Yes
    """

    # Define the filename column for storing the name of the uploaded file
    filename = db.Column(db.String(255), nullable=False)
    """
    filename: The name of the uploaded file.
    - Type: String
    - Maximum Length: 255 characters
    - Nullable: No (this field is required)
    """

    # Define the filepath column for storing the file's path on the server
    filepath = db.Column(db.String(255), nullable=False)
    """
    filepath: The full path where the file is stored on the server.
    - Type: String
    - Maximum Length: 255 characters
    - Nullable: No (this field is required)
    """

    # Define the timestamp column for storing the file's upload date and time
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    """
    uploaded_at: The timestamp of when the file was uploaded.
    - Type: DateTime
    - Default: The current UTC time (automatically set when a new record is created)
    """
