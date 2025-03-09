import streamlit as st

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Student Resource Portal",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Custom CSS to match the design in the example
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid #444;
        margin-bottom: 2rem;
    }
    .resource-section {
        background-color: #2D2D2D;
        padding: 1.5rem;
        border-radius: 5px;
        margin-bottom: 1.5rem;
    }
    .resource-header {
        border-bottom: 2px solid #FF5252;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .find-resources-btn {
        background-color: #FF5252;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 4px;
        cursor: pointer;
        text-align: center;
        display: block;
        margin: 1rem auto;
        font-weight: bold;
    }
    .tab-container {
        margin-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF5252 !important;
        color: white !important;
    }
    .download-btn {
        color: #FF5252;
        text-decoration: none;
    }
    .sidebar-content {
        background-color: #2D2D2D;
        padding: 1rem;
        border-radius: 5px;
    }
    .admin-btn {
        background-color: #333;
        border: 1px solid #FF5252;
        color: white;
        text-align: center;
        padding: 0.5rem;
        border-radius: 4px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Page configuration was already set at the top of the file

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

# Main header
st.markdown('<div class="main-header"><h1>Student Resource Portal</h1><p>Access past exams, study sheets, and helpful tips</p></div>', unsafe_allow_html=True)

# Sidebar content
with st.sidebar:
    # Display logo if available
    try:
        with open("assets/logo.svg", "r") as f:
            svg = f.read()
            st.image(svg, width=200)
    except:
        pass
    
    st.markdown('<h2>StudyHub</h2>', unsafe_allow_html=True)
    
    # Admin Login/Logout Section
    cols = st.columns([1, 1])
    if not st.session_state.is_admin:
        # Login button that opens a modal
        with cols[1]:
            if st.button("Admin Portal", key="admin_login"):
                st.session_state.show_login = True
                
        # Login modal
        if st.session_state.get('show_login', False):
            with st.form("login_form"):
                st.subheader("Admin Login")
                admin_username = st.text_input("Username")
                admin_password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                
                if submitted:
                    if admin_username == "llouay26" and admin_password == "LouayX2006@":  # Custom admin credentials
                        st.session_state.is_admin = True
                        st.session_state.show_login = False
                        st.success("Logged in as admin!")
                        st.rerun()
                    else:
                        st.error("Incorrect username or password!")
    else:
        with cols[1]:
            if st.button("Logout"):
                st.session_state.is_admin = False
                st.rerun()

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
    
    # Student view - Find Study Resources section
    st.markdown('<div class="resource-section"><h2 class="resource-header">Find Study Resources</h2>', unsafe_allow_html=True)
    
    # Create three columns for university, semester, and course selection
    col1, col2, col3 = st.columns(3)
    
    # University selection
    universities = settings.get("universities", [])
    if not universities:
        st.warning("No universities available. Admin needs to add universities.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    with col1:
        st.markdown("<p>Select University</p>", unsafe_allow_html=True)
        selected_uni = st.selectbox("University", universities, label_visibility="collapsed")
    
    # Semester selection
    semesters = settings.get("semesters", {}).get(selected_uni, [])
    if not semesters:
        st.warning(f"No semesters available for {selected_uni}. Admin needs to add semesters.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    with col2:
        st.markdown("<p>Select Semester</p>", unsafe_allow_html=True)
        selected_semester = st.selectbox("Semester", semesters, label_visibility="collapsed")
    
    # Course selection
    courses = settings.get("courses", {}).get(f"{selected_uni}_{selected_semester}", [])
    if not courses:
        st.warning(f"No courses available for {selected_uni}, {selected_semester}. Admin needs to add courses.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    with col3:
        st.markdown("<p>Select Course</p>", unsafe_allow_html=True)
        selected_course = st.selectbox("Course", courses, label_visibility="collapsed")
    
    # Find Resources button
    btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 2])
    with btn_col2:
        find_resources = st.button("Find Resources", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display resources if all selections are made
    if selected_uni and selected_semester and selected_course:
        st.markdown(f"<div class='resource-section'><h2>Resources for {selected_course}</h2>", unsafe_allow_html=True)
        
        # Create tabs container with custom CSS
        st.markdown('<div class="tab-container">', unsafe_allow_html=True)
        
        # Define tabs for different resource types
        tab1, tab2, tab3 = st.tabs(["Past Exams", "Study Sheets", "Tips & Guides"])
        
        # Generate file path for resources
        resource_path = get_file_path(selected_uni, selected_semester, selected_course)
        create_directory_if_not_exists(resource_path)
        
        # Display exams
        with tab1:
            exam_path = resource_path / "exams"
            create_directory_if_not_exists(exam_path)
            
            exams = os.listdir(exam_path) if os.path.exists(exam_path) else []
            if exams:
                for exam in exams:
                    col1, col2, col3 = st.columns([1, 3, 1])
                    file_path = exam_path / exam
                    with col1:
                        # Generate thumbnail preview
                        if exam.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            # For images, show a smaller version
                            st.image(file_path, width=80)
                        elif exam.lower().endswith(('.pdf')):
                            # For PDFs, show a PDF icon
                            st.markdown("📄", unsafe_allow_html=True)
                        else:
                            # For other files show a generic file icon
                            st.markdown("📁", unsafe_allow_html=True)
                    
                    with col2:
                        download_link = file_download_link(file_path, exam)
                        # Add custom class to style download link
                        styled_link = download_link.replace('<a href', '<a class="download-btn" href')
                        st.markdown(styled_link, unsafe_allow_html=True)
                        
                        # Only show file rename option for logged-in admins (in student view)
                        if st.session_state.is_admin and st.button("Rename", key=f"rename_exam_{exam}"):
                            st.session_state[f"rename_exam_{exam}_active"] = True
                        
                        if st.session_state.get(f"rename_exam_{exam}_active", False):
                            with st.form(key=f"rename_form_exam_{exam}"):
                                new_name = st.text_input("New filename:", value=exam)
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.form_submit_button("Save"):
                                        if new_name != exam:
                                            # Get file extension
                                            _, file_extension = os.path.splitext(exam)
                                            if not new_name.endswith(file_extension):
                                                new_name += file_extension
                                            
                                            # Rename the file
                                            new_file_path = exam_path / new_name
                                            os.rename(file_path, new_file_path)
                                            st.success(f"Renamed to {new_name}")
                                            st.session_state[f"rename_exam_{exam}_active"] = False
                                            st.rerun()
                                with col_b:
                                    if st.form_submit_button("Cancel"):
                                        st.session_state[f"rename_exam_{exam}_active"] = False
                                        st.rerun()
                    
                    with col3:
                        file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
                        st.caption(f"Uploaded: {file_date}")
            else:
                st.markdown("<p>No exams found for this selection.</p>", unsafe_allow_html=True)
        
        # Display study sheets
        with tab2:
            sheets_path = resource_path / "sheets"
            create_directory_if_not_exists(sheets_path)
            
            sheets = os.listdir(sheets_path) if os.path.exists(sheets_path) else []
            if sheets:
                for sheet in sheets:
                    col1, col2, col3 = st.columns([1, 3, 1])
                    file_path = sheets_path / sheet
                    with col1:
                        # Generate thumbnail preview
                        if sheet.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            # For images, show a smaller version
                            st.image(file_path, width=80)
                        elif sheet.lower().endswith(('.pdf')):
                            # For PDFs, show a PDF icon
                            st.markdown("📄", unsafe_allow_html=True)
                        else:
                            # For other files show a generic file icon
                            st.markdown("📁", unsafe_allow_html=True)
                    
                    with col2:
                        download_link = file_download_link(file_path, sheet)
                        # Add custom class to style download link
                        styled_link = download_link.replace('<a href', '<a class="download-btn" href')
                        st.markdown(styled_link, unsafe_allow_html=True)
                        
                        # Only show file rename option for logged-in admins (in student view)
                        if st.session_state.is_admin and st.button("Rename", key=f"rename_sheet_{sheet}"):
                            st.session_state[f"rename_sheet_{sheet}_active"] = True
                        
                        if st.session_state.get(f"rename_sheet_{sheet}_active", False):
                            with st.form(key=f"rename_form_sheet_{sheet}"):
                                new_name = st.text_input("New filename:", value=sheet)
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.form_submit_button("Save"):
                                        if new_name != sheet:
                                            # Get file extension
                                            _, file_extension = os.path.splitext(sheet)
                                            if not new_name.endswith(file_extension):
                                                new_name += file_extension
                                            
                                            # Rename the file
                                            new_file_path = sheets_path / new_name
                                            os.rename(file_path, new_file_path)
                                            st.success(f"Renamed to {new_name}")
                                            st.session_state[f"rename_sheet_{sheet}_active"] = False
                                            st.rerun()
                                with col_b:
                                    if st.form_submit_button("Cancel"):
                                        st.session_state[f"rename_sheet_{sheet}_active"] = False
                                        st.rerun()
                    
                    with col3:
                        file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
                        st.caption(f"Uploaded: {file_date}")
            else:
                st.markdown("<p>No study sheets found for this selection.</p>", unsafe_allow_html=True)
        
        # Display tips and notes
        with tab3:
            tips_path = resource_path / "tips"
            create_directory_if_not_exists(tips_path)
            
            tips = os.listdir(tips_path) if os.path.exists(tips_path) else []
            if tips:
                for tip in tips:
                    col1, col2, col3 = st.columns([1, 3, 1])
                    file_path = tips_path / tip
                    with col1:
                        # Generate thumbnail preview
                        if tip.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                            # For images, show a smaller version
                            st.image(file_path, width=80)
                        elif tip.lower().endswith(('.pdf')):
                            # For PDFs, show a PDF icon
                            st.markdown("📄", unsafe_allow_html=True)
                        else:
                            # For other files show a generic file icon
                            st.markdown("📁", unsafe_allow_html=True)
                    
                    with col2:
                        download_link = file_download_link(file_path, tip)
                        # Add custom class to style download link
                        styled_link = download_link.replace('<a href', '<a class="download-btn" href')
                        st.markdown(styled_link, unsafe_allow_html=True)
                        
                        # Only show file rename option for logged-in admins (in student view)
                        if st.session_state.is_admin and st.button("Rename", key=f"rename_tip_{tip}"):
                            st.session_state[f"rename_tip_{tip}_active"] = True
                        
                        if st.session_state.get(f"rename_tip_{tip}_active", False):
                            with st.form(key=f"rename_form_tip_{tip}"):
                                new_name = st.text_input("New filename:", value=tip)
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    if st.form_submit_button("Save"):
                                        if new_name != tip:
                                            # Get file extension
                                            _, file_extension = os.path.splitext(tip)
                                            if not new_name.endswith(file_extension):
                                                new_name += file_extension
                                            
                                            # Rename the file
                                            new_file_path = tips_path / new_name
                                            os.rename(file_path, new_file_path)
                                            st.success(f"Renamed to {new_name}")
                                            st.session_state[f"rename_tip_{tip}_active"] = False
                                            st.rerun()
                                with col_b:
                                    if st.form_submit_button("Cancel"):
                                        st.session_state[f"rename_tip_{tip}_active"] = False
                                        st.rerun()
                    
                    with col3:
                        file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')
                        st.caption(f"Uploaded: {file_date}")
            else:
                st.markdown("<p>No tips or guides found for this selection.</p>", unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
