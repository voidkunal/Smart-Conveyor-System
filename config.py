import os
import streamlit as st

STREAM_URL = 0

DATA_DIR = "data"
ALERTS_DIR = "alerts"
MODELS_DIR = "models"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ALERTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Securely pull from Streamlit Secrets
MONGO_URI = st.secrets["MONGO_URI"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = st.secrets["SMTP_EMAIL"]
SMTP_PASSWORD = st.secrets["SMTP_PASSWORD"]