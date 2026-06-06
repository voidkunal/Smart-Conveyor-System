import streamlit as st
import pandas as pd
import plotly.express as px
import time
from database import users_col, billing_col, maintenance_col, attendance_col
from components import render_chat_interface 

def generate_next_staff_id():
    users = list(users_col.find({"Staff ID": {"$regex": "^EMP"}}))
    if not users: return "EMP001"
    max_id = 0
    for u in users:
        try:
            num = int(u['Staff ID'].replace("EMP", ""))
            if num > max_id: max_id = num
        except: pass
    return f"EMP{max_id + 1:03d}"

def render_metric_card(title, value, color="#1e90ff"):
    return f"""
    <div style="background-color: #1a1c24; padding: 20px; border-radius: 12px; border-left: 5px solid {color}; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <p style="color: #a0a0a5; font-size: 0.95rem; font-weight: 600; text-transform: uppercase; margin: 0;">{title}</p>
        <h2 style="color: white; margin: 5px 0 0 0; font-size: 2.5rem; font-weight: 800;">{value}</h2>
    </div>
    """

def render_admin_dashboard():
    st.markdown("""
    <div style='background-color: #1a1c24; padding: 20px; border-radius: 12px; border-left: 5px solid #00e676; margin-bottom: 20px;'>
        <h2 style='margin: 0; color: white;'> Admin <span style='color: #00e676;'></span> Analytics </h2>
        <p style='margin: 0; color: #a0a0a5; font-size: 0.9rem;'>System Control, Staff Management, and Overview</p>
    </div>
    """, unsafe_allow_html=True)
    
    if maintenance_col is not None:
        active_lockdown = maintenance_col.find_one({"Status": "UNRESOLVED"})
        if active_lockdown:
            st.markdown(f"""
            <div style='background-color: rgba(255, 75, 75, 0.15); border: 1px solid #ff4b4b; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center;'>
                <h3 style='color: #ff4b4b; margin-top: 0;'>FACTORY FLOOR LOCKED</h3>
                <p style='color: white;'>{active_lockdown['Warning Type']} occurred at {active_lockdown['Time']}.</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Issue Resolved (Unlock System)", type="primary", use_container_width=True):
                maintenance_col.update_many({"Status": "UNRESOLVED"}, {"$set": {"Status": "RESOLVED"}})
                st.success("System Unlocked. Maintenance scanning can resume.")
                time.sleep(1)
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Analytics", "Staff List", "Add Staff", "Terminate", "Notifications"])
    
    with tabs[0]:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: st.markdown(render_metric_card("Active Staff", users_col.count_documents({"Status": "Active"}), "#1e90ff"), unsafe_allow_html=True)
        with col2: st.markdown(render_metric_card("Items Scanned", billing_col.count_documents({}), "#00e676"), unsafe_allow_html=True)
        with col3: st.markdown(render_metric_card("Total Alerts", maintenance_col.count_documents({}), "#ffaa00"), unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("<h5 style='color: #e0e0e0;'>Staff Status Distribution</h5>", unsafe_allow_html=True)
            staff_data = list(users_col.find({}, {"Status": 1, "_id": 0}))
            if staff_data:
                fig_pie = px.pie(pd.DataFrame(staff_data), names='Status', hole=0.5, color_discrete_sequence=['#1e90ff', '#262730'])
                fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_pie, use_container_width=True)

        with chart_col2:
            st.markdown("<h5 style='color: #e0e0e0;'>Maintenance Alerts by Type</h5>", unsafe_allow_html=True)
            alert_data = list(maintenance_col.find({}, {"Warning Type": 1, "_id": 0}))
            if alert_data:
                alert_counts = pd.DataFrame(alert_data)['Warning Type'].value_counts().reset_index()
                alert_counts.columns = ['Defect Type', 'Count']
                fig_bar = px.bar(alert_counts, x='Defect Type', y='Count', template="plotly_dark", color_discrete_sequence=['#ffaa00'])
                fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("<h5 style='color: #e0e0e0; margin-top: 20px;'>Scan Activity Over Time</h5>", unsafe_allow_html=True)
        billing_data = list(billing_col.find({}, {"Time": 1, "_id": 0}))
        if billing_data:
            df_billing = pd.DataFrame(billing_data)
            df_billing['Time'] = pd.to_datetime(df_billing['Time'], format='%H:%M:%S', errors='coerce').dt.strftime('%H:%M')
            scan_counts = df_billing['Time'].value_counts().sort_index().reset_index()
            scan_counts.columns = ['Time (HH:MM)', 'Items Scanned']
            fig_line = px.line(scan_counts, x='Time (HH:MM)', y='Items Scanned', markers=True, template="plotly_dark")
            fig_line.update_traces(fill='tozeroy', line_color='#00e676', fillcolor='rgba(0, 230, 118, 0.1)')
            fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_line, use_container_width=True)

       
        st.markdown("---")
        st.markdown("<h4 style='color: #e0e0e0;'>Raw Data Logs & Database Management</h4>", unsafe_allow_html=True)
        data_tab1, data_tab2 = st.tabs(["Billing Logs", "Maintenance Logs"])
        
        with data_tab1:
            billing_records_raw = list(billing_col.find({}).sort("_id", -1).limit(50))
            if billing_records_raw:
                display_records = []
                for r in billing_records_raw:
                    r_copy = r.copy()
                    r_copy["_id"] = str(r_copy["_id"]) 
                    display_records.append(r_copy)
                st.dataframe(pd.DataFrame(display_records), use_container_width=True)
                
                delete_options = { f"[{r.get('Time', 'N/A')}] {r.get('Product Name', 'Unknown')}": r['_id'] for r in billing_records_raw }
                col_del1, col_del2 = st.columns([3, 1])
                with col_del1: selected_to_delete = st.selectbox("Select item to permanently remove:", list(delete_options.keys()))
                with col_del2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Delete Record", use_container_width=True):
                        billing_col.delete_one({"_id": delete_options[selected_to_delete]})
                        st.success("Deleted!")
                        time.sleep(1)
                        st.rerun()
            else: st.info("No billing data available yet.")
                
        with data_tab2:
            maintenance_records_raw = list(maintenance_col.find({}).sort("_id", -1).limit(50))
            if maintenance_records_raw:
                display_maint_records = []
                for r in maintenance_records_raw:
                    r_copy = r.copy()
                    r_copy["_id"] = str(r_copy["_id"])
                    display_maint_records.append(r_copy)
                st.dataframe(pd.DataFrame(display_maint_records), use_container_width=True)
                
                maint_delete_options = { f"[{r.get('Time', 'N/A')}] {r.get('Warning Type', 'Unknown')}": r['_id'] for r in maintenance_records_raw }
                col_del3, col_del4 = st.columns([3, 1])
                with col_del3: maint_selected_to_delete = st.selectbox("Select alert to remove:", list(maint_delete_options.keys()), key="m_sel")
                with col_del4:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Delete Alert", use_container_width=True, key="m_btn"):
                        maintenance_col.delete_one({"_id": maint_delete_options[maint_selected_to_delete]})
                        st.success("Deleted!")
                        time.sleep(1)
                        st.rerun()
            else: st.info("No maintenance alerts recorded yet.")

    with tabs[1]:
        st.markdown("<br>", unsafe_allow_html=True)
        active_staff = list(users_col.find({"Status": "Active"}, {"_id": 0, "Address": 0, "Blood Group": 0}))
        if active_staff:
            df = pd.DataFrame(active_staff)
            cols = ['Staff ID', 'Name', 'Role', 'Current_State', 'Email', 'Phone']
            df = df[[c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else: st.info("No active staff found.")

    with tabs[2]:
        st.markdown("<br>", unsafe_allow_html=True)
        next_id = generate_next_staff_id()
        st.info(f"Assigned Staff ID: **{next_id}**")
        
        with st.form("add_staff_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Staff ID", value=next_id, disabled=True) 
                new_name = st.text_input("Full Name*")
                new_email = st.text_input("Gmail Address (For OTP)*")
                new_phone = st.text_input("Phone Number*")
            with col2:
                new_role = st.selectbox("Role*", ["Client Staff", "Maintenance Staff", "Admin"])
                new_age = st.number_input("Age", min_value=18, max_value=80, step=1)
                new_blood = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                new_address = st.text_area("Home Address")
                
            if st.form_submit_button("➕ Register New Staff", type="primary", use_container_width=True):
                if not new_name or not new_email or not new_phone:
                    st.error("Please fill in all mandatory (*) fields.")
                elif users_col.find_one({"$or": [{"Email": new_email}, {"Phone": new_phone}]}):
                    st.error("Email or Phone is already registered!")
                else:
                    users_col.insert_one({
                        "Staff ID": next_id, "Name": new_name, "Role": new_role, "Email": new_email,
                        "Phone": new_phone, "Age": new_age, "Blood Group": new_blood,
                        "Address": new_address, "Status": "Active", "Current_State": "Offline"
                    })
                    st.success(f"Employee {new_name} added successfully!")
                    time.sleep(1)
                    st.rerun()

    with tabs[3]:
        st.markdown("<br>", unsafe_allow_html=True)
        active_employees = list(users_col.find({"Status": "Active", "Staff ID": {"$ne": "admin"}}))
        
        if not active_employees:
            st.success("There are currently no active regular staff members to terminate.")
        else:
            employee_options = [f"{emp['Staff ID']} - {emp['Name']} ({emp['Role']})" for emp in active_employees]
            with st.form("terminate_form"):
                selected_employee_str = st.selectbox("Select Active Staff Member", employee_options)
                confirm = st.checkbox("I confirm I want to permanently terminate this employee's access.")
                if st.form_submit_button("Revoke Access", use_container_width=True):
                    if confirm and selected_employee_str:
                        term_id = selected_employee_str.split(" ")[0]
                        users_col.update_one({"Staff ID": term_id}, {"$set": {"Status": "Terminated", "Current_State": "Offline"}})
                        st.success(f"Access Revoked: {selected_employee_str}.")
                        time.sleep(1)
                        st.rerun()
                    elif not confirm: st.warning("Check the confirmation box to proceed.")

    with tabs[4]:
        st.markdown("<br>", unsafe_allow_html=True)
        render_chat_interface()