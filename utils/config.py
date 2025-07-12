# utils/config.py
import os
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai

def configure_gemini():
    """Configure the Gemini AI model with API key"""
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash")

# ✅ TEMPORARY test block
if __name__ == "__main__":
    load_dotenv()
    print("Loaded GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))

def generate_text_response(model, prompt):
    """Generate text response from Gemini model"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Error generating text response: {e}")

def generate_image_response(model, image, prompt):
    """Generate image analysis response from Gemini model"""
    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        raise Exception(f"Error generating image response: {e}")