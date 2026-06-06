import streamlit as st
import pandas as pd
import datetime
import time
from product_detector import ConveyorMonitor
from database import billing_col
from streamlit_webrtc import (
    webrtc_streamer,
    VideoTransformerBase,
    RTCConfiguration,
    WebRtcMode,
)
import av

# Standard Google servers to bypass cloud firewalls
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

class ClientVideoProcessor(VideoTransformerBase):
    def __init__(self):
        # Initialize the AI model inside the video thread
        self.monitor = ConveyorMonitor()
        self.new_products = [] # Temporary storage for items to send to the cart

    def recv(self, frame):
        # Convert browser frame to OpenCV format
        img = frame.to_ndarray(format="bgr24")
        
        # Run YOLO detection
        processed_img, state = self.monitor.process_frame(img)
        
        # If new products are billed, save them to be picked up by the UI
        if state["products"]:
            self.new_products.extend(state["products"])
            
        # Send processed frame back to browser
        return av.VideoFrame.from_ndarray(processed_img, format="bgr24")

def render_client_dashboard():
    st.markdown("""
    <div style='background-color: #1a1c24; padding: 20px; border-radius: 12px; border-left: 5px solid #1e90ff; margin-bottom: 25px;'>
        <h2 style='margin: 0; color: white;'>Client Terminal <span style='color: #1e90ff;'></span></h2>
        <p style='margin: 0; color: #a0a0a5; font-size: 0.9rem;'>Real-time AI Billing with Tracking</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'cart' not in st.session_state: st.session_state.cart = []

    tabs = st.tabs(["Terminal", "Notifications"])
    
    with tabs[0]:
        col1, col_space, col2 = st.columns([2.2, 0.1, 1.2])
        
        with col1:
            st.markdown("<h4 style='color: #e0e0e0;'>Live Conveyor Feed (Cloud Scanner)</h4>", unsafe_allow_html=True)
            
            # The WebRTC Cloud Camera replaces the old toggle and cv2 loop
            webrtc_ctx = webrtc_streamer(
    key="client_scanner",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    video_processor_factory=ClientVideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
) #new update
            
        with col2:
            st.markdown("<h4 style='color: #e0e0e0;'>Cart</h4>", unsafe_allow_html=True)
            
            cart_table = st.empty()
            total_placeholder = st.empty()
            
            # Extract data from the WebRTC thread into the main Streamlit thread
            if webrtc_ctx.state.playing and webrtc_ctx.video_processor:
                if len(webrtc_ctx.video_processor.new_products) > 0:
                    for best_product in webrtc_ctx.video_processor.new_products:
                        new_item = { "Product Name": best_product["name"], "Price (₹)": best_product["price"], "Time": datetime.datetime.now().strftime("%H:%M:%S") }
                        st.session_state.cart.append(new_item)
                    # Clear the processor queue after adding to cart
                    webrtc_ctx.video_processor.new_products = []
                    st.rerun() # Refresh the UI immediately to show new item
            
            if st.session_state.cart:
                df = pd.DataFrame(st.session_state.cart)
                display_cols = ["Product Name", "Price (₹)", "Time"]
                cart_table.dataframe(df[display_cols], use_container_width=True, hide_index=True)
                
                total = sum(item['Price (₹)'] for item in st.session_state.cart)
                total_placeholder.markdown(f"""
                <div style='background: linear-gradient(135deg, #1e90ff 0%, #0077ff 100%); padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(30, 144, 255, 0.3); margin-top: 10px;'>
                    <p style='margin: 0; color: rgba(255,255,255,0.8); font-size: 0.9rem; font-weight: 600; text-transform: uppercase;'>Total Amount</p>
                    <h2 style='color: white; margin: 0; font-size: 2.2rem;'>₹ {total:.2f}</h2>
                </div>
                <br>
                """, unsafe_allow_html=True)
            else:
                cart_table.markdown("""
                <div style='background-color: #262730; padding: 30px; border-radius: 8px; text-align: center; border: 1px dashed #444;'>
                    <p style='color: #888; margin: 0;'>Waiting for object to cross Target Zone...</p>
                </div>
                """, unsafe_allow_html=True)
                
            if len(st.session_state.cart) > 0:
                col_a, col_b = st.columns(2)
                if col_a.button("Pay", use_container_width=True, type="primary"):
                    if billing_col is not None:
                        billing_col.insert_many(st.session_state.cart)
                    st.success(f"Payment successful! Saved {len(st.session_state.cart)} items.")
                    st.session_state.cart = [] 
                    time.sleep(1)
                    st.rerun()
                    
                if col_b.button("Cancel", use_container_width=True):
                    st.session_state.cart = []
                    st.error("Transaction Cancelled.")
                    time.sleep(1)
                    st.rerun()

    with tabs[1]:
        st.markdown("<br>", unsafe_allow_html=True)
        from components import render_chat_interface
        render_chat_interface()