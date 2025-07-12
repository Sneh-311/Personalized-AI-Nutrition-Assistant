import streamlit as st
from utils.config import configure_gemini
from modules.text_input import handle_text_input 
from modules.image_input import handle_image_input 
from modules.personalized_health_assistant import handle_health_assistant_input
# Initialize Gemini model
model = configure_gemini()

st.set_page_config(page_title="AI Nutrition Assistant", layout="wide")
st.title("🍲The Smart AI Nutrition Assistant")

# Create tabs
tab1, tab2 , tab3 = st.tabs(["📝 Nutrition Planner", "📈 Food Analysis", "🩺 Personalized Health Assistant with RAG"])

# Process inputs in respective tabs
with tab1:
    st.subheader("Personalized Nutrition Plan")
    handle_text_input(model)

with tab2:
    st.subheader("Food Image Analysis")
    handle_image_input(model)

with tab3:
    st.subheader("Personalized Health Assistant with RAG")
    handle_health_assistant_input(model)
    