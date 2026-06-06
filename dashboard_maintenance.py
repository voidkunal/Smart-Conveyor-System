import streamlit as st
import pandas as pd
import datetime
import time
from product_detector import ConveyorMonitor
from database import maintenance_col, messages_col
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import av

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

class MaintenanceVideoProcessor(VideoTransformerBase):
    def __init__(self):
        self.monitor = ConveyorMonitor()
        self.new_alerts = []

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        processed_img, state = self.monitor.process_frame(img)
        
        if state["alerts"]:
            self.new_alerts.extend(state["alerts"])
            
        return av.VideoFrame.from_ndarray(processed_img, format="bgr24")

def render_maintenance_dashboard():
    st.markdown("""
    <div style='background-color: #1a1c24; padding: 20px; border-radius: 12px; border-left: 5px solid #ffaa00; margin-bottom: 25px;'>
        <h2 style='margin: 0; color: white;'>Maintenance <span style='color: #ffaa00;'></span></h2>
        <p style='margin: 0; color: #a0a0a5; font-size: 0.9rem;'>Detection & System Locks</p>
    </div>
    """, unsafe_allow_html=True)
    
    active_lockdown = None
    if maintenance_col is not None:
        active_lockdown = maintenance_col.find_one({"Status": "UNRESOLVED"})

    if active_lockdown:
        st.markdown(f"""
        <div style='background-color: rgba(255, 75, 75, 0.1); border: 2px solid #ff4b4b; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='color: #ff4b4b; margin: 0;'>EMERGENCY SYSTEM LOCK</h3>
            <p style='color: #e0e0e0; margin-top: 5px; font-size: 1.1rem;'>
                <strong>Cause:</strong> {active_lockdown['Warning Type']} detected at {active_lockdown['Time']}.<br>
                <span style='color: #a0a0a5; font-size: 0.9rem;'>Scanning disabled until Admin resolves the issue</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    tabs = st.tabs(["Inspection", "Notification"])
    
    with tabs[0]:
        col1, col_space, col2 = st.columns([2, 0.1, 1.2])
        with col1:
            st.markdown("<h4 style='color: #e0e0e0;'>Live Inspection Feed</h4>", unsafe_allow_html=True)
            
            # Disable the camera feed if the system is locked
            if active_lockdown:
                st.error("SYSTEM LOCKED BY ADMIN - Camera Disabled.")
            else:
                webrtc_ctx = webrtc_streamer(
                    key="maintenance_scanner",
                    mode=1, 
                    rtc_configuration=RTC_CONFIGURATION,
                    video_processor_factory=MaintenanceVideoProcessor,
                    media_stream_constraints={"video": True, "audio": False},
                    async_processing=True,
                )
            
        with col2:
            st.markdown("<h4 style='color: #e0e0e0;'>Alerts</h4>", unsafe_allow_html=True)
            alerts_table = st.empty()
            
            # Extract alert data from the WebRTC thread
            if not active_lockdown and webrtc_ctx.state.playing and webrtc_ctx.video_processor:
                if len(webrtc_ctx.video_processor.new_alerts) > 0:
                    critical_alerts = [a for a in webrtc_ctx.video_processor.new_alerts if "CRITICAL:" in a]
                    
                    if critical_alerts and maintenance_col is not None:
                        first_alert = critical_alerts[0]
                        time_str = datetime.datetime.now().strftime("%H:%M:%S")
                        
                        record = {
                            'Warning Type': first_alert.replace("CRITICAL: ", ""), 
                            'Severity': 'Critical', 
                            'Time': time_str,
                            'Estimated Cost': 1000 if 'Jam' in first_alert else 500, 
                            'Status': 'UNRESOLVED'
                        }
                        maintenance_col.insert_one(record)

                        if messages_col is not None:
                            messages_col.insert_one({
                                "sender_id": "SYS_AUTO",
                                "sender_name": "Safety Sensor Alpha",
                                "sender_role": "System",
                                "target_group": "Admin",
                                "text": f"EMERGENCY LOCK: {record['Warning Type']} detected on conveyor belt.",
                                "timestamp": datetime.datetime.now()
                            })
                        
                        webrtc_ctx.video_processor.new_alerts = []
                        st.rerun() # Refresh to show the lockdown screen immediately
            
            # Display recent history
            if maintenance_col is not None:
                recent_history = list(maintenance_col.find({}, {"_id": 0}).sort("_id", -1).limit(10))
                if recent_history:
                    df = pd.DataFrame(recent_history)
                    alerts_table.dataframe(df[["Warning Type", "Time", "Status"]], use_container_width=True, hide_index=True)
                else:
                    alerts_table.markdown("""
                    <div style='background-color: rgba(0, 255, 128, 0.05); padding: 20px; border-radius: 8px; text-align: center; border: 1px solid rgba(0, 255, 128, 0.2);'>
                        <h3 style='color: #00e676; margin: 0;'>✓</h3>
                        <p style='color: #888; margin: 0;'>No Alerts</p>
                    </div>
                    """, unsafe_allow_html=True)
            
    with tabs[1]:
        st.markdown("<br>", unsafe_allow_html=True)
        from components import render_chat_interface
        render_chat_interface()