import datetime
import streamlit as st
from database import attendance_col, users_col

def log_login(staff_id):
    login_time = datetime.datetime.now()
    
    
    if users_col is not None:
        users_col.update_one({"Staff ID": staff_id}, {"$set": {"Current_State": "Online"}})
        
        
        attendance_col.insert_one({
            'Staff ID': staff_id,
            'Login Time': login_time,
            'Logout Time': None,
            'Session Duration (Hours)': 0
        })

def log_logout(staff_id):
    logout_time = datetime.datetime.now()
    
    if attendance_col is not None and users_col is not None:
        
        users_col.update_one({"Staff ID": staff_id}, {"$set": {"Current_State": "Offline"}})
        
        
        record = attendance_col.find_one({"Staff ID": staff_id, "Logout Time": None})
        if record:
            duration_sec = (logout_time - record['Login Time']).total_seconds()
            hours = round(duration_sec / 3600, 2)
            
            attendance_col.update_one(
                {"_id": record["_id"]},
                {"$set": {
                    "Logout Time": logout_time,
                    "Session Duration (Hours)": hours
                }}
            )