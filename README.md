# **Corporatica Flask Application**

## **Overview**
Corporatica is a Flask-based web application designed for processing, analyzing, and visualizing various data types, including tabular data, images, and text. It offers a variety of endpoints for CRUD operations, statistical analysis, data visualizations, and text processing.

---

## **Features**
1. **Tabular Data**:
   - Upload and manage CSV/Excel files.
   - Perform CRUD operations.
   - Compute statistics (mean, median, mode, quartiles, and outliers).
   - Generate visualizations (bar, line, pie charts).

2. **Textual Data**:
   - Summarize text.
   - Extract keywords.
   - Perform sentiment analysis.
   - Generate T-SNE visualizations for text clusters.

3. **Image Processing**:
   - Upload and manage images.
   - Generate color histograms.
   - Create segmentation masks.
   - Manipulate images (resize, crop, convert formats).

---

## **Installation**

### **Prerequisites**
- Python 3.10 or later
- Docker (for containerization)
- PostgreSQL (optional for local database testing)

### **1. Install Dependencies**
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/corporatica.git
   cd corporatica
2.Install Python dependencies:

    pip install -r requirements.txt
### ***Running the Application (Locally)
1. Set Up Environment Variables
    Set the Flask app environment variable:
        $env:FLASK_APP="run.py"  # For Windows
        export FLASK_APP="run.py"  # For Linux/Mac
2. Start the Flask Application
        Run the Flask server:  flask run
3. Access the Application
        Navigate to http://127.0.0.1:5000 in your browser.



### ~**~Running the Application (Using Docker)
    1. Build the Docker Image
    Build the Docker container: docker-compose build
    2. Start the Containers
    Run the Docker containers: docker-compose up
    3. Access the Application
    Navigate to http://localhost:5000 in your browser.


### attached postman collection in folder postman 


#### Technologies Used
    Backend: Flask, SQLAlchemy
    Database: PostgreSQL
    Visualization: Matplotlib
    Text Processing: NLTK, TextBlob
    Image Processing: Pillow, NumPy
    Containerization: Docker, Docker Compose