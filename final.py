from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image
import time  # For rate-limiting requests

app = Flask(__name__)

# Replace with your actual Gemini API Key
GENAI_API_KEY = "AIzaSyAVGzRDrghkqNNprtSKa9Hu8JfSqvmR-dM"

# Configure Google Gemini AI API
genai.configure(api_key=GENAI_API_KEY)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file chosen"}), 400
    
    try:
        # Convert file to an image
        image = Image.open(file.stream)

        # Call Gemini AI API to generate description
        description = call_gemini_model(image)

        # Generate recommendations dynamically
        recommendations = generate_recommendations(description)

        return jsonify({
            "description": description,
            "recommendations": recommendations
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def call_gemini_model(image):
    """
    Calls Gemini AI model to generate a description of the landmark.
    Adds a delay to prevent hitting API rate limits.
    """
    try:
        time.sleep(1)  # Prevents hitting quota too fast
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content([image])
        return response.text if response else "No description available."
    except Exception as e:
        if "429" in str(e):
            return "Error: API quota exceeded. Try again later."
        return f"Error: {str(e)}"

def generate_recommendations(description):
    """
    Dynamically generates recommendations using the AI model based on the landmark description.
    Formats the output into a point-wise structure.
    """
    try:
        prompt = f"""
        Based on this landmark description, provide a well-structured list of nearby attractions and food recommendations.
        The response should be formatted as follows:
        
        **Nearby Attractions:**
        1. Attraction 1 - Short description
        2. Attraction 2 - Short description
        3. Attraction 3 - Short description
        
        **Food Recommendations:**
        1. Restaurant 1 - Popular dish
        2. Restaurant 2 - Popular dish
        3. Restaurant 3 - Popular dish
        
        Landmark Description: {description}
        """

        time.sleep(1)  # Prevents hitting quota too fast
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Ensuring a structured response
        return response.text.replace("\n", "<br>") if response else "No specific recommendations found."
    
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
