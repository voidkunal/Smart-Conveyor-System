# Smart-Conveyor-System
Techno India University final year project 2022 to 2026 Batch, Smart Conveyor System. 


🚀 Smart Conveyor System
An AI-powered, IoT-integrated industrial monitoring solution designed to automate product detection, billing, and maintenance tracking in real-time.
📋 Table of Contents
Overview
Key Features
Tech Stack
System Architecture
Installation
Usage
Contact
🌐 Overview
The Smart Conveyor System is a final-year Computer Science project aimed at modernizing factory workflows. By leveraging Computer Vision and edge processing, the system monitors conveyor belts to detect products, calculate billing metrics, and alert maintenance staff to potential hardware issues, all managed through a centralized web dashboard.
⚡ Key Features
Real-Time AI Detection: Uses YOLOv8 for high-precision product identification and conveyor monitoring.
Automated Billing: Automatically calculates billing data based on detected product counts and categories.
Role-Based Access Control (RBAC): Dedicated dashboards for Admins, Client Staff, and Maintenance Staff.
Live Analytics: Interactive visualizations using Plotly and Streamlit for real-time factory insights.
Cloud Synchronization: Securely stores logs and metrics in MongoDB Atlas with encrypted connections.
Cinematic UI: A custom glassmorphic dashboard built with Streamlit and CSS for a modern, professional experience.
🛠 Tech Stack
Frontend: Streamlit (UI/Dashboard)
AI/ML: OpenCV, YOLOv8 (Ultralytics), Python
Backend/Database: MongoDB (Atlas), Pandas
DevOps/Deployment: GitHub, Streamlit Cloud
Hardware Integration: IoT-capable Python scripts
🏗 System Architecture
The system captures video streams via localized edge hardware, performs inference locally to ensure privacy, and transmits metadata to the cloud for dashboard visualization.
⚙️ Installation
Clone the repository:
Bash
git clone https://github.com/voidkunal/Smart-Conveyor-System.git
cd smart-conveyor-system
Setup virtual environment:
Bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
Install dependencies:
Bash
pip install -r requirements.txt
Environment Variables:
Create a .streamlit/secrets.toml file and add your MongoDB connection string and SMTP credentials:
Ini, TOML
[mongo]
uri = "your_mongodb_connection_string"
🚀 Usage
Launch the application:
Bash
streamlit run app.py
Login: Use your assigned Staff ID to access the dashboard.
Monitor: Navigate to the "Client Mode" tab to view real-time conveyor throughput and detection logs.
📧 Contact
Kunal Mandal
Role: B.Tech (CSE-AI) Student, Techno India University
GitHub: voidkunal