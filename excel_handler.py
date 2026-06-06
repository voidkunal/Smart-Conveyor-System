import pandas as pd
import os
import io
import streamlit as st
from config import DATA_DIR
from database import users_col, attendance_col, billing_col, maintenance_col

def export_to_excel(cursor, filename):
    filepath = os.path.join(DATA_DIR, filename)
    data_list = list(cursor)
    
    if data_list:
        for item in data_list:
            item.pop('_id', None)
        df = pd.DataFrame(data_list)
        df.to_excel(filepath, index=False)
        return True
    return False

def get_excel_bytes(cursor):
    data_list = list(cursor)
    if data_list:
        for item in data_list:
            item.pop('_id', None)
        df = pd.DataFrame(data_list)
        output = io.BytesIO()
        df.to_excel(output, index=False)
        return output.getvalue()
    return None

def export_all_system_data():
    export_to_excel(users_col.find(), "staff_metadata.xlsx")
    export_to_excel(attendance_col.find(), "attendance_log.xlsx")
    export_to_excel(billing_col.find(), "billing_records.xlsx")
    export_to_excel(maintenance_col.find(), "maintenance_alerts.xlsx")