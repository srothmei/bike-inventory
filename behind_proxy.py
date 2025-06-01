import os
import logging
from streamlit_webrtc import RTCConfiguration

def is_behind_proxy():
    """
    Detect if the application is running behind a proxy based on environment variables.
    Returns True if the app is detected to be running behind a proxy.
    """
    return os.getenv('STREAMLIT_SERVER_HEADLESS', 'false').lower() == 'true'

def configure_webrtc_options():
    """
    Configure WebRTC options based on whether we're behind a proxy or not.
    Returns appropriate options dict for webrtc_streamer.
    """
    # Basic configuration
    options = {
        "media_stream_constraints": {"video": True, "audio": False},
        "async_processing": True,
    }
    
    # Create the RTC configuration
    ice_servers = [
        {"urls": ["stun:stun.l.google.com:19302"]}
    ]
    
    if is_behind_proxy():
        # Add more STUN servers for redundancy when behind a proxy
        ice_servers.extend([
            {"urls": ["stun:stun1.l.google.com:19302"]},
            {"urls": ["stun:stun2.l.google.com:19302"]},
            {"urls": ["stun:stun3.l.google.com:19302"]},
            {"urls": ["stun:stun4.l.google.com:19302"]}
        ])
        # Additional options for proxy environments
        options["video_html_attrs"] = {"controls": True, "autoPlay": True}
        options["media_stream_constraints"]["video"] = {
            "width": {"ideal": 640},
            "height": {"ideal": 480},
            "frameRate": {"ideal": 15}
        }
    
    # Create and return the RTCConfiguration object
    rtc_config = RTCConfiguration({"iceServers": ice_servers})
    return rtc_config, options
    
    return options

def log_proxy_status():
    """Log whether the app is running behind a proxy"""
    if is_behind_proxy():
        logging.info("Application is running behind a proxy. Using adjusted WebRTC configuration.")
    else:
        logging.info("Application is running directly (not behind a proxy).")
        
def get_webrtc_context_options():
    """Get the appropriate options for webrtc_streamer contexts"""
    rtc_configuration, options = configure_webrtc_options()
    return rtc_configuration, options
