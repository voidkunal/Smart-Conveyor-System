import streamlit as st
import base64
import os
from database import setup_default_admin, users_col
from auth import render_login
from attendance import log_logout
from excel_handler import export_all_system_data
from dashboard_client import render_client_dashboard
from dashboard_maintenance import render_maintenance_dashboard
from dashboard_admin import render_admin_dashboard
from export_reports import render_export_dashboard
from components import render_header, render_footer

st.set_page_config(page_title="Industrial Automation Hub", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_video_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as video_file:
                video_bytes = video_file.read()
            return base64.b64encode(video_bytes).decode()
    except Exception as e:
        print(f"Video load error: {e}")
    return None

def inject_cinematic_css():
    
    is_authenticated = st.session_state.get('current_user') is not None
    video_path = "bg_dashboard.mp4" if is_authenticated else "bg_login.mp4"
    
    
    encoded_video = load_video_base64(video_path)
    
    
    video_html = ""
    if encoded_video:
        video_html = f"""
        <video autoplay muted loop playsinline id="bg-video" style="position: fixed; right: 0; bottom: 0; min-width: 100vw; min-height: 100vh; z-index: -2; object-fit: cover; filter: brightness(0.25);">
            <source src="data:video/mp4;base64,{encoded_video}" type="video/mp4">
        </video>
        """

    
    st.markdown(f"""
    {video_html}
    <style>
    /* Global Transparent App Background */
    .stApp {{ 
        background-color: transparent !important;
        background: transparent !important;
        color: #ffffff; 
        font-family: 'Inter', -apple-system, sans-serif;
    }}
    
    /* Hide top padding */
    .block-container {{ padding-top: 2rem !important; }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}

    /* Transparent Sidebar with Blur */
    [data-testid="stSidebar"] {{
        background-color: rgba(15, 17, 21, 0.65) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255,255,255,0.05);
    }}

    /* Form & Container Styling (Glassmorphism Cards) */
    [data-testid="stForm"], .stDataFrame, div[data-testid="stVerticalBlock"] > div[style*="background-color"] {{ 
        background-color: rgba(26, 28, 36, 0.7) !important; 
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.1) !important; 
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important; 
        border-radius: 12px !important;
    }}

    /* Input Fields */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {{
        background-color: rgba(38, 39, 48, 0.6) !important; 
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        transition: 0.2s ease;
    }}
    div[data-baseweb="input"] > div:focus-within, div[data-baseweb="select"] > div:focus-within {{
        border: 1px solid #1e90ff !important;
        background-color: rgba(43, 44, 54, 0.9) !important;
    }}
    div[data-baseweb="input"] input {{ background-color: transparent !important; color: #ffffff !important; padding: 12px 16px !important; }}

    /* Buttons */
    button[kind="primary"] {{
        background: linear-gradient(135deg, #1e90ff 0%, #0077ff 100%) !important;
        color: white !important;
        border-radius: 24px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: 0.3s ease;
    }}
    button[kind="primary"]:hover {{
        box-shadow: 0 4px 20px rgba(30, 144, 255, 0.6) !important;
        transform: translateY(-2px);
    }}
    
    button[kind="secondary"] {{
        background-color: rgba(255,255,255,0.05) !important;
        backdrop-filter: blur(5px);
        color: #1e90ff !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 24px !important;
        font-weight: 600 !important;
    }}
    button[kind="secondary"]:hover {{
        background-color: rgba(255,255,255,0.1) !important;
        color: white !important;
    }}

    .subtext {{ color: #b0b0b5; font-size: 1.1rem; text-align: center; margin-bottom: 2rem; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }}
    </style>
    """, unsafe_allow_html=True)

setup_default_admin()


if 'current_user' not in st.session_state: st.session_state.current_user = None
if 'billing_data' not in st.session_state: st.session_state.billing_data = []
if 'maintenance_data' not in st.session_state: st.session_state.maintenance_data = []
if 'current_page' not in st.session_state: st.session_state.current_page = "home" 

def main():
    
    if not st.session_state.current_user and "user" in st.query_params:
        restored_id = st.query_params["user"]
        if restored_id == "admin":
            st.session_state.current_user = {
                'Staff ID': 'admin', 'Name': 'System Admin', 'Role': 'Admin', 'Email': 'offline@localhost', 'Phone':'000'
            }
        else:
            user = users_col.find_one({"Staff ID": restored_id})
            if user:
                st.session_state.current_user = user
    
    
    
    inject_cinematic_css()
    
    
    if not st.session_state.current_user:
        
        col_logo, col_space, col_home, col_policy, col_btn = st.columns([2, 4, 1, 1, 1.5])
        with col_logo:
            st.markdown("<h3 style='margin:0; padding-top:5px; font-weight:800; text-shadow: 0 2px 5px rgba(0,0,0,0.8);'>Kunal</h3>", unsafe_allow_html=True)
        
        with col_home:
            if st.button("Home", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
        with col_policy:
            if st.button("Policy", use_container_width=True):
                st.session_state.current_page = "policy"
                st.rerun()
        with col_btn:
            if st.button("Log In", type="primary", use_container_width=True):
                st.session_state.current_page = "login"
                st.rerun()

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        
        if st.session_state.current_page == "home":
            st.markdown("<h1 style='text-align: center; font-size: 4.5rem; font-weight: 800; margin-bottom: 0px; text-shadow: 0 4px 10px rgba(0,0,0,0.8);'>Industrial Automation System</h1>", unsafe_allow_html=True)
            st.markdown("<p class='subtext'>Access, monitor, and<br>protect your factory product with Customise AI.</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_spacer1, col_action1, col_spacer2 = st.columns([3, 4, 3])
            with col_action1:
                st.markdown("<div style='text-align: center;'><p style='color: #b0b0b5; text-shadow: 0 1px 3px rgba(0,0,0,0.8);'>System strictly restricted to authorized staff.</p></div>", unsafe_allow_html=True)
                if st.button("Login", type="primary", use_container_width=True):
                    st.session_state.current_page = "login"
                    st.rerun()

        elif st.session_state.current_page == "policy":
            col_spacer1, col_policy, col_spacer2 = st.columns([1, 4, 1])
            with col_policy:
                st.markdown("""
                <div style='background: rgba(26, 28, 36, 0.85); padding: 40px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(15px);'>
                    <h2 style='margin-top: 0;'>Data Security & Privacy Policy</h2>
                    <hr style='border-color: rgba(255,255,255,0.1);'>
                    <p><strong>1. Local Edge Processing:</strong> All computer vision inference is processed locally on Edge Hardware. Video feeds are never streamed to external cloud providers.</p>
                    <p><strong>2. Database Security:</strong> Metrics and attendance logs are securely transmitted to MongoDB Atlas using encrypted SSL/TLS connections.</p>
                    <p><strong>3. Authentication:</strong> Login requests utilize OTPs dispatched via secure SMTP.</p>
                </div>
                """, unsafe_allow_html=True)

        elif st.session_state.current_page == "login":
            col_spacer1, col_login, col_spacer2 = st.columns([1.5, 2, 1.5])
            with col_login:
                st.markdown("<h2 style='text-align: center; margin-bottom: 5px; text-shadow: 0 2px 5px rgba(0,0,0,0.8);'>Welcome Back</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center; color: #b0b0b5; margin-bottom: 30px; text-shadow: 0 1px 3px rgba(0,0,0,0.8);'>Please enter your credentials to log in</p>", unsafe_allow_html=True)
                
                render_login()
                
        
        st.markdown("""
        <div style="position: fixed; bottom: 20px; left: 0; width: 100%; text-align: center; color: rgba(255,255,255,0.5); font-size: 0.8rem; text-shadow: 0 1px 2px rgba(0,0,0,0.8);">
            © Kunal Mandal Custom Build Application 2026. All rights reserved.
        </div>
        """, unsafe_allow_html=True)
        
    
    else:
        render_header()
        user_role = st.session_state.current_user.get('Role', 'Client Staff')
        user_id = st.session_state.current_user.get('Staff ID', 'Unknown')
        
        st.sidebar.title(f"{st.session_state.current_user.get('Name', 'User')}")
        st.sidebar.markdown(f"**ID:** `{user_id}`<br>**Role:** {user_role}<br><span style='color: #00e676;'>● Online</span>", unsafe_allow_html=True)
        st.sidebar.markdown("---")
        
        menu_options = ["Logout"]
        if user_role == "Admin":
            menu_options = ["Admin Analytics", "Client Mode", "Maintenance Mode", "Export Reports", "Logout"]
        elif user_role == "Client Staff":
            menu_options = ["Client Mode", "Logout"]
        elif user_role == "Maintenance Staff":
            menu_options = ["Maintenance Mode", "Logout"]
            
        choice = st.sidebar.radio("Navigation Menu", menu_options)
        
        if choice == "Admin Analytics": render_admin_dashboard()
        elif choice == "Client Mode": render_client_dashboard()
        elif choice == "Maintenance Mode": render_maintenance_dashboard()
        elif choice == "Export Reports": render_export_dashboard()
        elif choice == "Logout":
            log_logout(user_id)
            export_all_system_data() 
            st.session_state.current_user = None
            st.session_state.current_page = "home" 
            st.query_params.clear() 
            st.rerun()
            
        render_footer()

if __name__ == "__main__":
    main()