from flask import Blueprint, request, jsonify
from app.models import UploadedFile
from app import db
import os
import pandas as pd
from config import Config
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Create a new blueprint for handling upload and processing of tabular data
bp = Blueprint('upload', __name__)

# Global variable to hold the uploaded dataframe
dataframe = None

# Ensure the upload folder exists
if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)

# Route to upload a CSV or Excel file
@bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a CSV or Excel file and store it in the upload folder.
    The file is loaded into a global pandas dataframe for further processing.
    """
    global dataframe
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        return jsonify({"error": "Unsupported file type"}), 400
    
    filepath = os.path.join(Config.UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # Load the uploaded file into a pandas dataframe
    if file.filename.endswith('.csv'):
        dataframe = pd.read_csv(filepath)
    elif file.filename.endswith('.xlsx'):
        dataframe = pd.read_excel(filepath)
    
    # Save file metadata in the database
    uploaded_file = UploadedFile(filename=file.filename, filepath=filepath)
    db.session.add(uploaded_file)
    db.session.commit()

    return jsonify({"message": "File uploaded successfully", "file_id": uploaded_file.id}), 201

# Route to compute basic statistics
@bp.route('/statistics', methods=['GET'])
def compute_statistics():
    """
    Compute basic statistics like mean, median, mode, quartiles, and outliers
    for numeric columns in the dataframe.
    """
    global dataframe
    if dataframe is None or dataframe.empty:
        return jsonify({"error": "No data available"}), 400

    numeric_df = dataframe.select_dtypes(include=['float64', 'int64'])

    if numeric_df.empty:
        return jsonify({"error": "No numeric data available"}), 400

    # Calculate statistics
    stats = {
        "mean": numeric_df.mean().to_dict(),
        "median": numeric_df.median().to_dict(),
        "mode": numeric_df.mode().iloc[0].to_dict() if not numeric_df.mode().empty else {},
        "quartiles": numeric_df.quantile([0.25, 0.5, 0.75]).to_dict(),
    }

    # Detect outliers using IQR
    outliers = {}
    for column in numeric_df.columns:
        Q1 = numeric_df[column].quantile(0.25)
        Q3 = numeric_df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers[column] = numeric_df[
            (numeric_df[column] < lower_bound) | (numeric_df[column] > upper_bound)
        ][column].tolist()

    stats["outliers"] = outliers

    return jsonify(stats)

# Route to read all records
@bp.route('/read', methods=['GET'])
def read_records():
    """
    Retrieve all records in the dataframe.
    """
    global dataframe
    if dataframe is None or dataframe.empty:
        return jsonify({"error": "No data available"}), 400

    try:
        records = dataframe.to_dict(orient='records')
        return jsonify(records), 200
    except Exception as e:
        return jsonify({"error": f"Error reading records: {str(e)}"}), 500

# Route to create a new record
@bp.route('/create', methods=['POST'])
def create_record():
    """
    Add a new record to the dataframe.
    """
    global dataframe
    new_record = request.json
    if not new_record:
        return jsonify({"error": "No data provided"}), 400

    try:
        new_row = pd.DataFrame([new_record])
        dataframe = pd.concat([dataframe, new_row], ignore_index=True)
        return jsonify({"message": "Record created successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Error creating record: {str(e)}"}), 500

# Route to update an existing record
@bp.route('/update', methods=['PUT'])
def update_record():
    """
    Update an existing record in the dataframe by index.
    """
    global dataframe
    update_params = request.json

    if not update_params or "index" not in update_params:
        return jsonify({"error": "Index is required"}), 400

    try:
        index = update_params["index"]

        if index < 0 or index >= len(dataframe):
            return jsonify({"error": "Index out of range"}), 400

        for column, value in update_params.items():
            if column != "index" and column in dataframe.columns:
                dataframe.at[index, column] = value

        return jsonify({"message": "Record updated successfully", "updated_record": dataframe.iloc[index].to_dict()}), 200
    except Exception as e:
        return jsonify({"error": f"Error updating record: {str(e)}"}), 500

# Route to delete a record
@bp.route('/delete', methods=['DELETE'])
def delete_record():
    """
    Delete a record from the dataframe by index.
    """
    global dataframe

    try:
        index = request.args.get("index", type=int)

        if index is None:
            return jsonify({"error": "Index is required"}), 400

        if index < 0 or index >= len(dataframe):
            return jsonify({"error": "Index out of range"}), 400

        deleted_record = dataframe.iloc[index].to_dict()

        dataframe = dataframe.drop(index=index).reset_index(drop=True)

        return jsonify({"message": "Record deleted successfully", "deleted_record": deleted_record}), 200
    except Exception as e:
        return jsonify({"error": f"Error deleting record: {str(e)}"}), 500

# Route to generate visualizations
@bp.route('/visualization', methods=['POST'])
def generate_chart():
    """
    Generate visualizations (bar, line, pie) for the dataframe.
    Input:
        - `chart_type`: Type of chart to generate (bar, line, pie).
        - `x_column`, `y_column`: Columns to use for the visualization.
    """
    global dataframe
    if dataframe is None or dataframe.empty:
        return jsonify({"error": "No data available"}), 400

    chart_type = request.json.get("chart_type", "bar")
    x_column = request.json.get("x_column")
    y_column = request.json.get("y_column")

    if not x_column or not y_column:
        return jsonify({"error": "x_column and y_column are required"}), 400

    try:
        plt.figure()
        if chart_type == "bar":
            dataframe.groupby(x_column)[y_column].mean().plot(kind="bar")
        elif chart_type == "line":
            dataframe.plot(x=x_column, y=y_column, kind="line")
        elif chart_type == "pie":
            dataframe.groupby(x_column)[y_column].sum().plot(kind="pie", autopct='%1.1f%%')

        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        img_data = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()

        return jsonify({"chart": img_data}), 200
    except Exception as e:
        return jsonify({"error": f"Error generating chart: {str(e)}"}), 500
