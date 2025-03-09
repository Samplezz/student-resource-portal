import streamlit as st
import pandas as pd
import os
import json
import base64
from datetime import datetime
from pathlib import Path
import shutil
from PIL import Image
import io

from utils import load_settings, save_settings, get_file_path, create_directory_if_not_exists
from admin import show_admin_panel

# Page configuration
st.set_page_config(
    page_title="Educational Resources Hub",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state if not already done
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()

# Create required directories
data_dir = Path("data")
uploads_dir = data_dir / "uploads"
create_directory_if_not_exists(data_dir)
create_directory_if_not_exists(uploads_dir)

# Sidebar content
with st.sidebar:
    st.title("📚 EduResources")
    
    # Display logo if available
    try:
        with open("assets/logo.svg", "r") as f:
            svg = f.read()
            st.image(svg, width=200)
    except:
        pass
    
    st.markdown("---")
    
    # Admin Login Section
    if not st.session_state.is_admin:
        with st.expander("Admin Login"):
            admin_password = st.text_input("Admin Password", type="password")
            if st.button("Login"):
                if admin_password == "admin123":  # Simple password for demo purposes
                    st.session_state.is_admin = True
                    st.success("Logged in as admin!")
                    st.experimental_rerun()
                else:
                    st.error("Incorrect password!")
    else:
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.experimental_rerun()
        st.success("Logged in as Admin")

def file_download_link(file_path, file_name):
    """Generate a download link for a file"""
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    file_size = os.path.getsize(file_path) / 1024  # Size in KB
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">Download {file_name} ({file_size:.1f} KB)</a>'

def main():
    # Main content
    settings = st.session_state.settings
    
    # If admin is logged in, show admin panel
    if st.session_state.is_admin:
        show_admin_panel()
        return
    
    # Student view
    st.title("Educational Resources Hub")
    st.markdown("""
    Welcome to the Educational Resources Hub! Access past exams, study sheets, and helpful tips for your courses.
    Use the dropdowns below to navigate to your university, semester, and course.
    """)
    
    # University selection
    universities = settings.get("universities", [])
    if not universities:
        st.warning("No universities available. Admin needs to add universities.")
        return
    
    selected_uni = st.selectbox("Select University", universities)
    
    # Semester selection
    semesters = settings.get("semesters", {}).get(selected_uni, [])
    if not semesters:
        st.warning(f"No semesters available for {selected_uni}. Admin needs to add semesters.")
        return
    
    selected_semester = st.selectbox("Select Semester", semesters)
    
    # Course selection
    courses = settings.get("courses", {}).get(f"{selected_uni}_{selected_semester}", [])
    if not courses:
        st.warning(f"No courses available for {selected_uni}, {selected_semester}. Admin needs to add courses.")
        return
    
    selected_course = st.selectbox("Select Course", courses)
    
    # Display resources if all selections are made
    if selected_uni and selected_semester and selected_course:
        st.markdown(f"## Resources for {selected_course}")
        
        # Define tabs for different resource types
        tab1, tab2, tab3 = st.tabs(["Exams", "Study Sheets", "Tips & Notes"])
        
        # Generate file path for resources
        resource_path = get_file_path(selected_uni, selected_semester, selected_course)
        create_directory_if_not_exists(resource_path)
        
        # Display exams
        with tab1:
            exam_path = resource_path / "exams"
            create_directory_if_not_exists(exam_path)
            
            exams = os.listdir(exam_path) if os.path.exists(exam_path) else []
            if exams:
                st.subheader("Available Exams")
                for exam in exams:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        file_path = exam_path / exam
                        st.markdown(file_download_link(file_path, exam), unsafe_allow_html=True)
                    with col2:
                        file_date = datetime.fromtimestamp(os.path.getmtime(exam_path / exam)).strftime('%Y-%m-%d')
                        st.caption(f"Uploaded: {file_date}")
            else:
                st.info("No exams available for this course yet.")
        
        # Display study sheets
        with tab2:
            sheets_path = resource_path / "sheets"
            create_directory_if_not_exists(sheets_path)
            
            sheets = os.listdir(sheets_path) if os.path.exists(sheets_path) else []
            if sheets:
                st.subheader("Available Study Sheets")
                for sheet in sheets:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        file_path = sheets_path / sheet
                        st.markdown(file_download_link(file_path, sheet), unsafe_allow_html=True)
                    with col2:
                        file_date = datetime.fromtimestamp(os.path.getmtime(sheets_path / sheet)).strftime('%Y-%m-%d')
                        st.caption(f"Uploaded: {file_date}")
            else:
                st.info("No study sheets available for this course yet.")
        
        # Display tips and notes
        with tab3:
            tips_path = resource_path / "tips"
            create_directory_if_not_exists(tips_path)
            
            tips = os.listdir(tips_path) if os.path.exists(tips_path) else []
            if tips:
                st.subheader("Available Tips & Notes")
                for tip in tips:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        file_path = tips_path / tip
                        st.markdown(file_download_link(file_path, tip), unsafe_allow_html=True)
                    with col2:
                        file_date = datetime.fromtimestamp(os.path.getmtime(tips_path / tip)).strftime('%Y-%m-%d')
                        st.caption(f"Uploaded: {file_date}")
            else:
                st.info("No tips or notes available for this course yet.")

# Run the app
if __name__ == "__main__":
    main()
