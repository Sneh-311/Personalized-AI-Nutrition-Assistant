import streamlit as st
from utils.medical_data import COMMON_CONDITIONS, COMMON_ALLERGIES
import sys
import os
from modules.display_plan import display_plan_with_tabs
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config import generate_text_response

def handle_text_input(model):
    """Handle all text input processing and display"""
    # Sidebar text input
    st.sidebar.header("Quick Input Option")
    user_text = st.sidebar.text_area(
        "Or enter your details here (health goals, conditions, preferences, etc.)", 
        height=150,
        key="sidebar_text"
    )
    
    # Main form input
    with st.expander("➕ Provide Your Details (Fill Form Below)", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Personal Details
            st.subheader("Personal Information")
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            gender = st.selectbox("Gender", ["Male", "Female"])
            lifestyle = st.selectbox("Lifestyle", ["Sedentary", "Moderately Active", "Very Active", "Athlete"])
        
        with col2:
            # Goals & Preferences
            st.subheader("Goals & Preferences")
            health_goals = st.multiselect(
                "Primary Health Goals",
                options=[
                    "Weight loss",
                    "Muscle gain",
                    "Improved digestion",
                    "Heart health",
                    "Diabetes management",
                    "Increased energy",
                    "Better sleep",
                    "Stress reduction",
                    "Improved athletic performance",
                    "Hormonal balance",
                    "Cholesterol management",
                    "Blood pressure control",
                    "Anti-inflammatory diet",
                    "Pregnancy nutrition",
                    "Postpartum recovery",
                    "Menopause support"
                ],
                default=["Weight loss"],
                help="Select all that apply"
            )
            fitness_routine = st.selectbox(
                "Current Fitness Routine",
                ["No exercise", "Light exercise", "Moderate exercise", "Intense exercise"]
            )
            dietary_preferences = st.multiselect(
                "Dietary Preferences",
                ["Vegetarian", "Vegan", "Pescatarian", "Gluten-free", 
                 "Dairy-free", "Keto", "Mediterranean", "Other"]
            )
            cooking_ability = st.select_slider("Cooking Skill Level", ["Beginner", "Intermediate", "Advanced"])
        
        with col3:
            # Health Conditions
            st.subheader("Health Information")
            medical_conditions = st.multiselect(
                "Medical Conditions",
                options=COMMON_CONDITIONS,
                default=[],
                help="Select all that apply",
                key="medical_conditions"
            )
            
            # Custom condition input
            other_condition = st.text_input(
                "Other Condition (specify)",
                key="other_condition",
                placeholder="Add condition not listed"
            )
            
            # Allergies Section
            allergies = st.multiselect(
                "Food Allergies/Intolerances",
                options=COMMON_ALLERGIES,
                default=[],
                help="Select all that apply",
                key="allergies"
            )
            
            # Custom allergy input
            other_allergy = st.text_input(
                "Other Allergy (specify)",
                key="other_allergy",
                placeholder="Add allergy not listed"
            )
            
            medications = st.text_area("Current Medications")

    # Generate button
    prompt = ""
    if st.button("Generate Personalized Nutrition Plan", type="primary"):
        with st.spinner("Creating your holistic nutrition plan..."):
            try:
                # Prepare data from form
                all_conditions = medical_conditions.copy()
                if other_condition:
                    all_conditions.append(other_condition)

                all_allergies = allergies.copy()
                if other_allergy:
                    all_allergies.append(other_allergy)
                
                # If user provided text input, use that primarily
                if user_text.strip():
                    prompt = f"""
                    Create a detailed nutrition plan based on the following information:
                    
                    USER PROVIDED TEXT:
                    {user_text}
                    """
                
                    # Use form data only if no text input
                if not health_goals:
                    st.warning("Please at least specify your health goals")
                    return
                    
                prompt += f"""
                    Create a detailed nutrition plan for:
                    - Age: {age}
                    - Gender: {gender}
                    - Conditions: {', '.join(all_conditions) if all_conditions else 'None'}
                    - Allergies: {', '.join(all_allergies) if all_allergies else 'None'}
                    - Medications: {medications if medications else 'None'}
                    - Goals: {', '.join(health_goals)}
                    - Fitness: {fitness_routine}
                    - Preferences: {', '.join(dietary_preferences) if dietary_preferences else 'None'}
                    - Cooking Skill: {cooking_ability}
                    - Lifestyle: {lifestyle}
                    - Country: India
                    
                    Provide a 7-day meal plan with:
                    - Breakfast, Lunch, Dinner, and Snacks
                    - Portion sizes
                    - Nutritional breakdown (calories, macros)
                    - Cooking instructions
                    - Grocery list

                    Requirements:
                    1. Avoid contraindications for: {', '.join(all_conditions) if all_conditions else 'None'}
                    2. Exclude: {', '.join(all_allergies) if all_allergies else 'None'}
                    3. Optimize for: {', '.join(health_goals)}
                    4. Match activity level: {fitness_routine}
                    
                    Please structure the response clearly with day-by-day sections.
                    === Day 1 ===
                    Breakfast: [meal name] - [portion]
                    - Ingredients: [list]
                    - Nutrition: [calories, macros]
                    - Instructions: [steps]

                    Lunch: [meal name] - [portion]
                    - Ingredients: [list]
                    - Nutrition: [calories, macros]
                    - Instructions: [steps]

                    Dinner: [meal name] - [portion]
                    - Ingredients: [list]
                    - Nutrition: [calories, macros]
                    - Instructions: [steps]

                    Snacks: [options]

                    === Day 2 ===
                    [repeat same structure]
                   
                    """
                
                response = generate_text_response(model, prompt)
                print(f"Generated response: {response}")  # Debugging output
                st.markdown("## 🌿 Your Holistic Nutrition Plan")
                st.markdown("---")
                if response:
                    display_plan_with_tabs(model, response)
            
            except Exception as e:
                st.error(f"Error generating plan: {str(e)}")
                return False
        
        return True
    return False