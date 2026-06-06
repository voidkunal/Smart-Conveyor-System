import streamlit as st
import datetime
from database import messages_col

def render_header():
    current_time = datetime.datetime.now().strftime("%I:%M %p | %b %d, %Y")
    st.markdown(f"""
    <div style='display: flex; justify-content: flex-end; padding: 5px 0; margin-bottom: 15px;'>
        <div style='background-color: transparent; padding: 6px 16px; border-radius: 20px; border: 1px solid #2b2c36;'>
            <span style='color: #a0a0a5; font-size: 0.85rem; font-weight: 500;'>
                Time : <span style='color: #1e90ff;'>{current_time}</span>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
        <br><hr style='border-color: #2b2c36;'>
        <div style='text-align: center; padding: 10px; color: #555; font-size: 12px; letter-spacing: 0.5px;'>
            &copy; Kunal Mandal Build AI Based Conveyor System | SECURED BY Advanced Security | Designed for Edge AI Excellence
        </div>
    """, unsafe_allow_html=True)

def render_chat_interface():
    st.markdown("""
    <div style='background-color: #1a1c24; padding: 15px; border-radius: 12px; border-left: 5px solid #00b4d8; margin-bottom: 15px;'>
        <h3 style='margin: 0; color: white; font-size: 1.2rem;'>Notifications</h3>
        <p style='margin: 0; color: #a0a0a5; font-size: 0.8rem;'>Encrypted Channel</p>
    </div>
    """, unsafe_allow_html=True)
    
    if messages_col is None:
        st.error("Database disconnected. Cannot load messages.")
        return

    current_role = st.session_state.current_user['Role']
    current_id = st.session_state.current_user['Staff ID']

    
    if current_role == "Admin":
        query = {} 
    else:
        
        query = {
            "$or": [
                {"target_group": "Global"},
                {"target_group": current_role},
                {"sender_id": current_id}
            ]
        }
        
    messages = list(messages_col.find(query).sort("timestamp", 1).limit(50))
    
    chat_container = st.container(height=400)
    with chat_container:
        if not messages:
            st.info("No messages in this channel yet.")
        for msg in messages:
            time_str = msg['timestamp'].strftime("%H:%M")
            is_me = msg['sender_id'] == current_id
            
            target = msg.get('target_group', 'Global')
            target_badge = f"<span style='font-size:10px; color:rgba(255,255,255,0.6);'>[To: {target}]</span>"
            
            if is_me:
                st.markdown(f"<div style='text-align: right; background: #1e90ff; color: white; padding: 12px; border-radius: 12px 12px 0 12px; margin-bottom: 8px; margin-left: 20%; box-shadow: 0 2px 5px rgba(0,0,0,0.2);'>{target_badge} <b>You</b> ({time_str})<br>{msg['text']}</div>", unsafe_allow_html=True)
            else:
                border_color = "#ff4b4b" if msg['sender_role'] == "Admin" else "#00e676"
                st.markdown(f"<div style='text-align: left; background: #262730; color: #e0e0e0; padding: 12px; border-radius: 12px 12px 12px 0; margin-bottom: 8px; margin-right: 20%; border-left: 4px solid {border_color}; box-shadow: 0 2px 5px rgba(0,0,0,0.2);'>{target_badge} <b style='color: white;'>{msg['sender_name']} [{msg['sender_role']}]</b> ({time_str})<br>{msg['text']}</div>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([2, 4, 1])
        
        with col1:
            
            if current_role == "Admin":
                options = ["Global", "Client Staff", "Maintenance Staff"]
            else:
                options = ["Admin"] 
            target = st.selectbox("Send to:", options, label_visibility="collapsed")
            
        with col2:
            new_msg = st.text_input("Message...", label_visibility="collapsed", placeholder="Type your message here...")
            
        with col3:
            submit = st.form_submit_button("Send", type="primary", use_container_width=True)
            
        if submit and new_msg.strip():
            messages_col.insert_one({
                "sender_id": current_id,
                "sender_name": st.session_state.current_user['Name'],
                "sender_role": current_role,
                "target_group": target,
                "text": new_msg.strip(),
                "timestamp": datetime.datetime.now()
            })
            st.rerun()