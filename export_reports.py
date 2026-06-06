import streamlit as st
from excel_handler import get_excel_bytes
from database import users_col, attendance_col, billing_col, maintenance_col

def render_export_dashboard():
    st.markdown("""
    <div style='background-color: #1a1c24; padding: 30px; border-radius: 12px; text-align: center; border: 1px solid #333; margin-top: 20px;'>
        <h1 style='font-size: 4rem; margin-bottom: 0;'>₹</h1>
        <h2 style='color: white; margin-top: 10px;'>System Backup & Export</h2>
        <p style='color: #a0a0a5; font-size: 1.1rem; max-width: 500px; margin: 10px auto 30px auto;'>
            Download individual system memory records into structured Excel files for offline safekeeping.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        users_data = get_excel_bytes(users_col.find())
        if users_data:
            st.download_button("Staff Metadata", data=users_data, file_name="staff_metadata.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.button("No Staff Data", disabled=True, use_container_width=True)
            
    with col2:
        attendance_data = get_excel_bytes(attendance_col.find())
        if attendance_data:
            st.download_button("Attendance Log", data=attendance_data, file_name="attendance_log.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.button("No Attendance Data", disabled=True, use_container_width=True)
            
    with col3:
        billing_data = get_excel_bytes(billing_col.find())
        if billing_data:
            st.download_button("Billing Records", data=billing_data, file_name="billing_records.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.button("No Billing Data", disabled=True, use_container_width=True)
            
    with col4:
        maintenance_data = get_excel_bytes(maintenance_col.find())
        if maintenance_data:
            st.download_button("Maintenance Alerts", data=maintenance_data, file_name="maintenance_alerts.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.button("No Maintenance Data", disabled=True, use_container_width=True)