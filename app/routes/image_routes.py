from flask import Blueprint, request, jsonify
import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Create a new blueprint for image-related routes
bp = Blueprint('images', __name__)

# Define the upload folder and ensure it exists
UPLOAD_FOLDER = 'files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route to upload one or multiple images
@bp.route('/upload_images', methods=['POST'])
def upload_images():
    """
    Upload one or multiple images.
    Supported formats: PNG, JPG, JPEG.
    Returns:
        - Success message with a list of saved files.
    """
    # Check if images are included in the request
    if 'images' not in request.files:
        return jsonify({"error": "No images provided"}), 400

    # Get all uploaded files
    uploaded_files = request.files.getlist('images')
    saved_files = []

    # Save each valid image
    for file in uploaded_files:
        if file.filename.endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            saved_files.append(file.filename)
        else:
            return jsonify({"error": f"Unsupported file type: {file.filename}"}), 400

    return jsonify({"message": "Images uploaded successfully", "files": saved_files}), 200

# Route to generate a color histogram for an image
@bp.route('/color_histogram', methods=['POST'])
def generate_color_histogram():
    """
    Generate a color histogram for an image.
    Input:
        - `image_file` (str): Name of the image file.
    Returns:
        - A base64-encoded image of the color histogram.
    """
    # Get the image file name from the request
    image_file = request.json.get('image_file')
    filepath = os.path.join(UPLOAD_FOLDER, image_file)

    # Check if the image exists
    if not os.path.exists(filepath):
        return jsonify({"error": "Image not found"}), 404

    try:
        # Open the image and convert it to a numpy array
        image = Image.open(filepath)
        image_array = np.array(image)

        # Plot histograms for each color channel (red, green, blue)
        plt.figure()
        for i, color in enumerate(['red', 'green', 'blue']):
            plt.hist(image_array[:, :, i].ravel(), bins=256, color=color, alpha=0.5)
        plt.xlabel('Pixel Intensity')
        plt.ylabel('Frequency')

        # Save the histogram as a base64-encoded image
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        img_data = base64.b64encode(img.getvalue()).decode('utf-8')
        plt.close()

        return jsonify({"histogram": img_data}), 200
    except Exception as e:
        return jsonify({"error": f"Error generating histogram: {str(e)}"}), 500

# Route to generate a segmentation mask for an image
@bp.route('/segmentation_mask', methods=['POST'])
def generate_segmentation_mask():
    """
    Generate a segmentation mask for an image based on a threshold.
    Input:
        - `image_file` (str): Name of the image file.
        - `threshold` (int): Pixel intensity threshold (default: 128).
    Returns:
        - A base64-encoded segmentation mask.
    """
    # Get the image file name and threshold from the request
    image_file = request.json.get('image_file')
    threshold = request.json.get('threshold', 128)

    filepath = os.path.join(UPLOAD_FOLDER, image_file)
    if not os.path.exists(filepath):
        return jsonify({"error": "Image not found"}), 404

    try:
        # Open the image, convert it to grayscale, and generate a mask
        image = Image.open(filepath).convert('L')
        image_array = np.array(image)
        mask = (image_array > threshold).astype(np.uint8) * 255

        # Save the mask as a base64-encoded image
        mask_image = Image.fromarray(mask)
        img = BytesIO()
        mask_image.save(img, format='PNG')
        img.seek(0)
        img_data = base64.b64encode(img.getvalue()).decode('utf-8')

        return jsonify({"segmentation_mask": img_data}), 200
    except Exception as e:
        return jsonify({"error": f"Error generating segmentation mask: {str(e)}"}), 500

# Route to manipulate an image (resize, crop, convert format)
@bp.route('/manipulate_image', methods=['POST'])
def manipulate_image():
    """
    Perform image manipulation tasks such as resizing, cropping, or format conversion.
    Input:
        - `image_file` (str): Name of the image file.
        - `operation` (str): The manipulation to perform (resize, crop, convert).
        - `params` (dict): Additional parameters for the operation.
    Returns:
        - A base64-encoded manipulated image.
    """
    # Get the image file name, operation, and parameters from the request
    image_file = request.json.get('image_file')
    operation = request.json.get('operation')
    params = request.json.get('params', {})

    filepath = os.path.join(UPLOAD_FOLDER, image_file)
    if not os.path.exists(filepath):
        return jsonify({"error": "Image not found"}), 404

    try:
        # Open the image
        image = Image.open(filepath)

        # Perform the requested operation
        if operation == 'resize':
            width = params.get('width')
            height = params.get('height')
            if not width or not height:
                return jsonify({"error": "Width and height are required for resizing"}), 400
            image = image.resize((width, height))
        elif operation == 'crop':
            left = params.get('left')
            top = params.get('top')
            right = params.get('right')
            bottom = params.get('bottom')
            if not all([left, top, right, bottom]):
                return jsonify({"error": "All crop parameters (left, top, right, bottom) are required"}), 400
            image = image.crop((left, top, right, bottom))
        elif operation == 'convert':
            format = params.get('format', 'PNG')
            img = BytesIO()
            image.save(img, format=format)
            img.seek(0)
            img_data = base64.b64encode(img.getvalue()).decode('utf-8')
            return jsonify({"converted_image": img_data}), 200
        else:
            return jsonify({"error": "Unsupported operation"}), 400

        # Save the manipulated image as a base64-encoded PNG
        img = BytesIO()
        image.save(img, format='PNG')
        img.seek(0)
        img_data = base64.b64encode(img.getvalue()).decode('utf-8')

        return jsonify({"manipulated_image": img_data}), 200
    except Exception as e:
        return jsonify({"error": f"Error manipulating image: {str(e)}"}), 500
