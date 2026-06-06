import streamlit as st
from pymongo import MongoClient
import certifi 
from config import MONGO_URI

@st.cache_resource
def init_db():
    try:
        ca = certifi.where()
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tlsCAFile=ca)
        client.admin.command('ping') 
        return client['smart_conveyor_db']
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

db = init_db()

if db is not None:
    users_col = db['users']
    attendance_col = db['attendance']
    billing_col = db['billing']
    maintenance_col = db['maintenance']
    messages_col = db['messages'] 
else:
    users_col = attendance_col = billing_col = maintenance_col = messages_col = None

def setup_default_admin():
    if users_col is not None and users_col.count_documents({}) == 0:
        users_col.insert_one({
            'Staff ID': 'admin', 'Name': 'System Admin', 'Role': 'Admin',
            'Email': 'your_personal@gmail.com', 'Phone': '+91 xxxxxxxxxx',
            'Age': 21, 'Blood Group': 'AB-', 'Address': 'Server Room', 'Status': 'Active'
        })