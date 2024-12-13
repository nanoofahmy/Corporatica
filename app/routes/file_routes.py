from flask import Blueprint, jsonify, send_file
from app.models import UploadedFile
import os

# Create a new blueprint for file-related routes
bp = Blueprint('file', __name__)

# Route to get all uploaded files from the database
@bp.route('/files', methods=['GET'])
def get_all_files():
    """
    Fetch all files stored in the database.
    Returns:
        - A JSON list of all files with their metadata (id, filename, filepath, uploaded_at).
    """
    # Query all files from the database
    files = UploadedFile.query.all()
    
    # Create a list of file metadata to return as a JSON response
    result = [{"id": file.id, "filename": file.filename, "filepath": file.filepath, "uploaded_at": file.uploaded_at} for file in files]
    
    # Return the result as a JSON response
    return jsonify(result)

# Route to download a specific file by its ID
@bp.route('/files/<int:file_id>', methods=['GET'])
def download_file(file_id):
    """
    Download a specific file by its ID.
    Params:
        - file_id (int): The ID of the file to download.
    Returns:
        - The requested file for download, or an error message if not found.
    """
    # Retrieve the file from the database using the given file_id
    file = UploadedFile.query.get(file_id)
    print("Downloading file", file)  # Log the file being downloaded

    # If the file is not found in the database, return a 404 error
    if not file:
        return jsonify({"error": "File not found in database"}), 404

    # Check if the file exists on the disk at the stored filepath
    if not os.path.exists(file.filepath):
        return jsonify({"error": f"File not found on disk: {file.filepath}"}), 404

    # Get the absolute path of the file to avoid relative path issues
    absolute_path = os.path.abspath(file.filepath)
    
    # Double-check if the file exists at the absolute path
    if not os.path.exists(absolute_path):
        return jsonify({"error": f"File not found on disk: {absolute_path}"}), 404

    # If the file exists, send it to the client for download
    return send_file(absolute_path, as_attachment=True)
