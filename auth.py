import streamlit as st
import smtplib
import random
from email.mime.text import MIMEText
from config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD
from database import users_col
from attendance import log_login

def send_otp_email(receiver_email, otp):
    try:
        msg = MIMEText(f"Your Secure Login OTP is: {otp}\n\nDo not share this.")
        msg['Subject'] = 'Login OTP - Smart Conveyor System'
        msg['From'] = SMTP_EMAIL
        msg['To'] = receiver_email

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

def render_login():
    if users_col is None:
        st.error("Cloud DB failed. Use Admin Offline Mode.")
        st.stop()
        
    if 'login_step' not in st.session_state:
        st.session_state.login_step = 1
        st.session_state.temp_user = None
        st.session_state.generated_otp = None
    if 'show_admin_view' not in st.session_state:
        st.session_state.show_admin_view = False

    
    if not st.session_state.show_admin_view:
        if st.session_state.login_step == 1:
            with st.form("verify_user_form"):
                st.markdown("<p style='color: #a0a0a5; font-size: 0.9rem; margin-bottom: 5px;'>Enter Registered Email or Phone Number</p>", unsafe_allow_html=True)
                user_identifier = st.text_input("identifier", label_visibility="collapsed")
                submit_btn = st.form_submit_button("Request OTP to Login", type="primary", use_container_width=True)
                
                if submit_btn:
                    user = users_col.find_one({
                        "$or": [{"Email": user_identifier}, {"Phone": user_identifier}],
                        "Status": "Active"
                    })
                    
                    if user:
                        otp = str(random.randint(100000, 999999))
                        if send_otp_email(user['Email'], otp):
                            st.session_state.temp_user = user
                            st.session_state.generated_otp = otp
                            st.session_state.login_step = 2
                            st.success(f"OTP sent securely to {user['Email']}")
                            st.rerun()
                    else:
                        st.error("Invalid Email/Phone or Account is Terminated.")
            
            
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("If you are Admin, click here", type="secondary", use_container_width=True):
                    st.session_state.show_admin_view = True
                    st.rerun()

        elif st.session_state.login_step == 2:
            with st.form("verify_otp_form"):
                st.info(f"Enter the 6-digit OTP sent to {st.session_state.temp_user['Email']}")
                entered_otp = st.text_input("Enter OTP", type="password")
                
                col_sub, col_can = st.columns(2)
                with col_sub:
                    if st.form_submit_button("Verify & Login", type="primary", use_container_width=True):
                        if entered_otp == st.session_state.generated_otp:
                            st.session_state.current_user = st.session_state.temp_user
                            st.query_params["user"] = st.session_state.current_user['Staff ID'] 
                            st.session_state.login_step = 1 
                            log_login(st.session_state.current_user['Staff ID'])
                            st.rerun()
                        else:
                            st.error("Invalid OTP.")
                with col_can:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.login_step = 1
                        st.rerun()

    
    else:
        with st.form("admin_bypass_form"):
            st.markdown("<p style='color: #a0a0a5; font-size: 0.9rem; margin-bottom: 5px;'>Admin Override Credentials</p>", unsafe_allow_html=True)
            admin_id = st.text_input("Admin ID", placeholder="ID")
            admin_pass = st.text_input("Password", type="password", placeholder="Password")
            
            if st.form_submit_button("Admin Login", type="primary", use_container_width=True):
                if admin_id == "admin" and admin_pass == "admin":
                    st.session_state.current_user = {
                        'Staff ID': 'admin', 'Name': 'System Admin', 'Role': 'Admin', 'Email': 'offline@localhost', 'Phone':'000'
                    }
                    st.query_params["user"] = "admin" 
                    log_login('admin')
                    st.rerun()
                else:
                    st.error("Invalid Offline Credentials")
                    
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⬅ Back to Staff Login", type="secondary", use_container_width=True):
                st.session_state.show_admin_view = False
                st.rerun()