import streamlit as st
from PIL import Image
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.config import generate_image_response

def handle_image_input(model):
    """Handle all image input processing and display"""
    st.sidebar.header("Image Input")
    uploaded_image = st.sidebar.file_uploader(
        "Upload a food image or grocery label", 
        type=["jpg", "jpeg", "png"]
    )
    
    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image",  
                 width=300,  # Fixed width in pixels
                 output_format="PNG"  )# Ensures consistent display)
        
        with st.spinner("Analyzing image and generating nutrition insights..."):
            try:
                prompt = "Analyze this image and describe the food content with nutrition details"
                response = generate_image_response(model, image, prompt)
                st.markdown("### 🧠 Food Analysis")
                st.write(response)
            except Exception as e:
                st.error(f"Error analyzing image: {e}")
                return False
        return True
    return False