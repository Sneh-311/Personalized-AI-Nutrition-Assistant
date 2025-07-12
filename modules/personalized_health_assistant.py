import streamlit as st
import pandas as pd
import os
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
from langchain_community.document_loaders import CSVLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from dotenv import load_dotenv
from utils.medical_data import COMMON_ALLERGIES
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def handle_health_assistant_input(model):
    st.markdown("""
                This assistant provides personalized health and dietary recommendations based on your health profile.
                Upload your health data (CSV) and answer a few questions to get started.
                """)    
    # File upload
    uploaded_file = st.file_uploader("Upload your health data (CSV)", type=["csv"])
    
    # Example CSV structure
    with st.expander("Expected CSV Format"):
        st.markdown("""
        Your CSV should contain health and nutritional information with columns like:
        - `Patient_ID`: Unique identifier
        - `Age`: Patient age
        - `Gender`: Male/Female/Other
        - `Height_cm`: Height in centimeters
        - `Weight_kg`: Weight in kilograms
        - `BMI`: Body Mass Index
        - `Chronic_Disease`: Any chronic diseases
        - `Blood_Pressure_Systolic/Diastolic`: Blood pressure readings
        - `Cholesterol_Level`: Total cholesterol
        - `Blood_Sugar_Level`: Glucose levels
        - `Genetic_Risk_Factor`: Any genetic risks
        - `Allergies`: Food allergies
        - `Daily_Steps`: Activity level
        - `Exercise_Frequency`: Weekly exercise frequency
        - `Sleep_Hours`: Average sleep duration
        - `Alcohol_Consumption`: Yes/No
        - `Smoking_Habit`: Yes/No
        - `Dietary_Habits`: Vegetarian/Non-vegetarian/etc.
        - `Caloric_Intake`: Daily calories
        - `Macronutrient_Intake`: Protein/Carbs/Fats
        - `Preferred_Cuisine`: Food preferences
        - `Food_Aversions`: Disliked foods
        - `Recommended_*`: Recommended nutritional values
        - `Recommended_Meal_Plan`: Suggested diet type
        """)
        example_data = {
            'Patient_ID': ['P00001'],
            'Age': [56],
            'Gender': ['Other'],
            'Height_cm': [163],
            'Weight_kg': [66],
            'BMI': [24.84],
            'Chronic_Disease': ['None'],
            'Blood_Pressure_Systolic': [175],
            'Blood_Pressure_Diastolic': [75],
            'Cholesterol_Level': [219],
            'Blood_Sugar_Level': [124],
            'Genetic_Risk_Factor': ['No'],
            'Allergies': ['None'],
            'Daily_Steps': [11452],
            'Exercise_Frequency': [5],
            'Sleep_Hours': [7.6],
            'Alcohol_Consumption': ['No'],
            'Smoking_Habit': ['Yes'],
            'Dietary_Habits': ['Vegetarian'],
            'Caloric_Intake': [2593],
            'Protein_Intake': [105],
            'Carbohydrate_Intake': [179],
            'Fat_Intake': [143],
            'Preferred_Cuisine': ['Western'],
            'Food_Aversions': ['None'],
            'Recommended_Calories': [2150],
            'Recommended_Protein': [108],
            'Recommended_Carbs': [139],
            'Recommended_Fats': [145],
            'Recommended_Meal_Plan': ['High-Protein Diet']
        }
        st.dataframe(pd.DataFrame(example_data))

    # Initialize session state
    if 'health_data' not in st.session_state:
        st.session_state.health_data = None
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    if 'qa_chain' not in st.session_state:
        st.session_state.qa_chain = None

    # Process uploaded file
    if uploaded_file is not None:
        try:
            # Read CSV file
            df = pd.read_csv(r"C:\Users\HP\Desktop\Personalised_Diet_Recommender\dataset\Personalized_Diet_Recommendations.csv")
            st.session_state.health_data = df
            
            # Save CSV temporarily for LangChain processing
            temp_file = "temp_health_data.csv"
            df.to_csv(temp_file, index=False)
            
            # Load documents
            loader = CSVLoader(file_path=temp_file)
            documents = loader.load()
            
            # Split documents
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)
            
            embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            st.session_state.vectorstore = FAISS.from_documents(texts, embeddings)
            
            # Create QA chain
            llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
            st.session_state.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=st.session_state.vectorstore.as_retriever(),
                verbose=True
            )
            
            st.success("Health data processed successfully!")
            
            # Show a sample of the data
            with st.expander("View uploaded health data"):
                st.dataframe(df.head())
                
        except Exception as e:
            st.error(f"Error processing file: {e}")
            if 'temp_file' in locals() and os.path.exists(temp_file):
                os.remove(temp_file)

    # User input form
    with st.form("user_input_form"):
        st.header("Tell us about your health and dietary needs")
        
        # Basic user info
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        with col3:
            weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
        
        # Health metrics
        col1, col2 = st.columns(2)
        with col1:
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
            bmi = st.number_input("BMI (calculated)", value=round(weight/((height/100)**2), 2), disabled=True)
        with col2:
            bp_systolic = st.number_input("Blood Pressure (Systolic)", min_value=50, max_value=250, value=120)
            bp_diastolic = st.number_input("Blood Pressure (Diastolic)", min_value=30, max_value=150, value=80)
        
        # Health indicators
        col1, col2 = st.columns(2)
        with col1:
            cholesterol = st.number_input("Cholesterol Level (mg/dL)", min_value=100, max_value=400, value=200)
            blood_sugar = st.number_input("Blood Sugar Level (mg/dL)", min_value=50, max_value=400, value=100)
        with col2:
            daily_steps = st.number_input("Daily Steps", min_value=0, max_value=50000, value=8000)
            exercise_freq = st.selectbox("Exercise Frequency (per week)", [0,1,2,3,4,5,6,7])
        
        # Lifestyle factors
        col1, col2, col3 = st.columns(3)
        with col1:
            sleep_hours = st.number_input("Sleep Hours (daily)", min_value=0, max_value=24, value=7)
        with col2:
            alcohol = st.selectbox("Alcohol Consumption", ["No", "Occasionally", "Regularly"])
        with col3:
            smoking = st.selectbox("Smoking Habit", ["No", "Yes"])
        
        # Dietary preferences
        col1, col2 = st.columns(2)
        with col1:
            diet_type = st.selectbox("Dietary Habits", ["Vegetarian", "Vegan", "Omnivore", "Pescatarian", "Keto", "Other"])
            preferred_cuisine = st.selectbox("Preferred Cuisine", ["Western", "Mediterranean", "Asian", "Indian", "Latin", "Other"])
        with col2:
            allergies = st.multiselect(
                "Food Allergies/Intolerances",
                options=COMMON_ALLERGIES,
                default=[],
                help="Select all that apply",
                key="allergies1"
            )
            aversions = st.text_input("Food Aversions (dislikes)", "")
        
        # Current concern
        health_concern = st.text_area("Describe your health concern or dietary question", 
                                    "I'm looking for dietary recommendations to improve my...")
        
        submitted = st.form_submit_button("Get Health & Dietary Advice")

    # Generate response when form is submitted
    if submitted and openai_api_key:
        if st.session_state.qa_chain is None:
            st.warning("Please upload a health data CSV file first")
        else:
            with st.spinner("Generating personalized health and dietary advice..."):
                try:
                    # Create context from user inputs
                    user_context = f"""
                    User Profile:
                    - Age: {age}
                    - Gender: {gender}
                    - Weight: {weight} kg
                    - Height: {height} cm
                    - BMI: {bmi}
                    - Blood Pressure: {bp_systolic}/{bp_diastolic}
                    - Cholesterol: {cholesterol} mg/dL
                    - Blood Sugar: {blood_sugar} mg/dL
                    - Activity Level: {daily_steps} steps/day
                    - Exercise Frequency: {exercise_freq} times/week
                    - Sleep: {sleep_hours} hours/night
                    - Alcohol: {alcohol}
                    - Smoking: {smoking}
                    - Diet Type: {diet_type}
                    - Preferred Cuisine: {preferred_cuisine}
                    - Allergies: {allergies}
                    - Food Aversions: {aversions}
                    
                    Health Concern: {health_concern}
                    """
                    
                    # Generate response using RAG
                    prompt = f"""
                    Based on the following user profile and health concern, provide:
                    1. Personalized health advice considering their metrics and lifestyle
                    2. Specific dietary recommendations including:
                       - Suggested daily caloric intake
                       - Macronutrient breakdown (protein, carbs, fats)
                       - Meal plan suggestions based on their dietary preferences
                       - Specific food recommendations considering allergies/aversions
                       - Recipes or meal ideas from their preferred cuisine
                    3. Lifestyle modification suggestions
                    
                    Be thorough but concise, and always recommend consulting a healthcare professional for serious concerns.
                    
                    {user_context}
                    
                    Answer:
                    """
                    
                    response = st.session_state.qa_chain.run(prompt)
                    
                    # Display response
                    st.subheader("Personalized Health & Dietary Advice")
                    st.markdown(response)
                    st.markdown("---")
                  
                    st.success("Advice generated successfully!")
                except Exception as e:
                    st.error(f"Error generating response: {e}")
    elif submitted and not openai_api_key:
        st.error("Please enter your OpenAI API key to generate responses")

    # Add some sample questions if no data is entered yet
    if st.session_state.health_data is None:
        st.markdown("---")
        st.subheader("Example Questions You Can Ask")
        st.markdown("""
        - What foods should I eat to lower my cholesterol?
        - I'm vegetarian with nut allergies - what high-protein foods can I eat?
        - Recommend a Mediterranean diet meal plan for someone with high blood pressure
        - What are some low-carb snack options for my keto diet?
        - Suggest balanced meals for a diabetic who prefers Asian cuisine
        - How can I increase my protein intake as a vegan?
        - What are good breakfast options for someone with gluten intolerance?
        """)