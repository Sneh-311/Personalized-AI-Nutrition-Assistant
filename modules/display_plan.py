import streamlit as st
import re
import re
import pandas as pd
from io import StringIO
# from utils.image_utils import generate_meal_image

def create_nutrition_summary(day_content):
    """Parse and calculate nutrition data"""
    nutrition_data = []
    pattern = r'([A-Za-z]+): (.+?) - (.+?)\n- Calories: (\d+)'
    for match in re.finditer(pattern, day_content):
        meal_type, name, portion, calories = match.groups()
        nutrition_data.append({
            'Meal': f"{meal_type}: {name}",
            'Portion': portion,
            'Calories': int(calories)
        })
    return pd.DataFrame(nutrition_data)

def display_day_tab(model, day_num, day_content):
    """Display content for a single day tab"""
    # Meal Plan Section
    st.subheader(f"📅 Day {day_num} Meal Plan")
    st.markdown(day_content.replace(' - ', '\n\n- '))
    
    # Nutrition Summary
    nutrition_df = create_nutrition_summary(day_content)
    if not nutrition_df.empty:
        st.subheader("🧮 Nutrition Summary")
        st.dataframe(nutrition_df.style.highlight_max(axis=0))
        st.caption(f"Total Calories: {nutrition_df['Calories'].sum()} kcal")
  
    # Download Button
    st.download_button(
        label="⬇️ Download Day Plan",
        data=day_content,
        file_name=f"day_{day_num}_plan.md",
        mime="text/markdown"
    )

def display_plan_with_tabs(model, plan_text):
    """Main display function with tabs"""
    # Tab Setup
    tab_icons = ["🍎", "🥑", "🥦", "🍗", "🐟", "🥗", "🍠"]
    tabs = st.tabs([f"{icon} Day {i+1}" for i, icon in enumerate(tab_icons)])
    
    # Full Plan Download
    st.sidebar.download_button(
        "🖨️ Export Full Plan",
        plan_text,
        "nutrition_plan_full.md"
    )
    
    # Day Content
    days = re.split(r'=== Day \d+ ===', plan_text)
    for i, tab in enumerate(tabs):
        with tab:
            if i < len(days)-1:
                display_day_tab(model, i+1, days[i+1].strip())
            else:
                st.warning("Content not generated for this day")
    
    # Additional Notes
    if len(days) > 8:
        st.markdown("## 📝 Additional Recommendations")
        st.markdown(days[0] + ''.join(days[8:]))