import json
import os
import base64
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request, send_file, send_from_directory
import google.generativeai as genai

# Initialize the Flask application
app = Flask(__name__)

# Set the Gemini API key
API_KEY = 'AIzaSyCBK_55snzIsVwJiMKg6LoxdcUIJAzL8Lc'
genai.configure(api_key=API_KEY)

# Configure the path for uploaded CVs
UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    return send_file('web/index.html')

@app.route("/api/generate", methods=["POST"])
def generate_api():
    try:
        # Handle the incoming form data
        job_position = request.form.get('job-position')
        cv_file = request.files['cv-upload']

        if not job_position or not cv_file:
            return jsonify({"error": "Job position and CV file are required"}), 400

        # Secure the filename and save the CV to the upload folder
        filename = secure_filename(cv_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cv_file.save(filepath)

        # Read the CV file content
        with open(filepath, 'rb') as file:
            cv_content = file.read()

        # Convert CV content to base64 for inclusion in the API request
        cv_base64 = base64.b64encode(cv_content).decode('utf-8')

        # Construct the prompt for CV analysis
        prompt = f"""
        You are a CV Analysis expert. Analyze the following CV based on the given criteria and provide a JSON response with the structure:
        {{
            "name": "<Candidate Name>",
            "score": "<Overall Score>",
            "criteria-detail": [
                {{
                    "criteria": "<Criteria Name>",
                    "score": "<Criteria Score>",
                    "description": "<Description of the evaluation>"
                }},
                ...
            ]
        }}
        Job: {job_position}
        Criteria:
        - Relevant work experience
        - Required skills
        - Educational background
        - Certifications
        - Achievements
        - Professionalism and formatting
        """

        # Use the Gemini API to analyze the CV based on the prompt
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")  # Replace with the correct model name

        # Prepare the content with the base64 encoded CV
        contents = [
            {
                "role": "user",
                "parts": [
                    {"inline_data": {"mime_type": cv_file.content_type, "data": cv_base64}},
                    {"text": prompt}
                ]
            }
        ]

        # Send the prompt and content to the Gemini API and get the response
        response = model.generate_content(contents)

        # Parse the response from the Gemini API
        result = response.result if hasattr(response, 'result') else response.text

        # Ensure the result is in JSON format
        result_json = json.loads(result)

        return jsonify(result_json)

    except Exception as e:
        # Print the exception to the logs
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('web', path)

if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 80)))
