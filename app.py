import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import threading
import queue
import os
import uuid
import tempfile
from pathlib import Path

from db import InventoryDB
from config import Config
from barcode_utils import enhanced_barcode_detection, analyze_image_quality, comprehensive_barcode_detection

# Initialize directory structure
Config.init_dirs()

# Use config for file paths
STATIC_DIR = Config.STATIC_DIR
IMAGE_DIR = Config.IMAGE_DIR

# iPhone Macro Camera Configuration
def get_iphone_camera_constraints():
    """Return camera constraints for iPhone macro mode."""
    # iPhone macro mode: high resolution, environment camera, no audio
    return {
        "video": {
            "width": {"min": 640, "ideal": 1920, "max": 4032},
            "height": {"min": 480, "ideal": 1440, "max": 3024},
            "facingMode": {"exact": "environment"},
            "focusMode": "continuous",
            "aspectRatio": {"ideal": 4/3},
            "frameRate": {"ideal": 30, "max": 60},
            # iPhone macro: get as close as possible
        },
        "audio": False
    }

def get_android_camera_constraints():
    """Get camera constraints optimized for Android macro mode"""
    return {
        "video": {
            "width": {"min": 640, "ideal": 1280, "max": 1920},
            "height": {"min": 480, "ideal": 720, "max": 1080},
            "facingMode": "environment",
            "focusMode": "continuous",  
            "focusDistance": {"min": 0.05, "ideal": 0.15, "max": 0.25},
            "zoom": {"min": 1.0, "ideal": 1.5, "max": 2.5},
            "aspectRatio": {"ideal": 16/9},
        },
        "audio": False
    }

class MacroCameraProcessor:
    """Processor for handling macro camera stream with barcode detection"""
    
    def __init__(self):
        self.result_queue = queue.Queue()
        self.detection_enabled = True
        self.last_detection_time = 0
        self.detection_cooldown = 2.0  # seconds between detections
    
    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Only process for barcode detection every few seconds to avoid overload
        current_time = time.time()
        if (self.detection_enabled and 
            current_time - self.last_detection_time > self.detection_cooldown):
            
            self.last_detection_time = current_time
            
            # Convert to PIL Image for barcode detection
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            
            # Quick barcode detection (non-blocking)
            try:
                barcodes, method, _ = enhanced_barcode_detection(pil_img, debug=False)
                
                if barcodes:
                    barcode_data = barcodes[0].data.decode('utf-8', errors='ignore')
                    self.result_queue.put({
                        'barcode': barcode_data,
                        'method': method,
                        'timestamp': current_time
                    })
            except Exception as e:
                pass  # Silently continue if detection fails
        
        # Add visual indicators for macro mode
        # Draw focus area rectangle
        h, w = img.shape[:2]
        center_x, center_y = w // 2, h // 2
        rect_size = min(w, h) // 3
        
        # Green rectangle for macro focus area
        cv2.rectangle(img, 
                     (center_x - rect_size//2, center_y - rect_size//2),
                     (center_x + rect_size//2, center_y + rect_size//2),
                     (0, 255, 0), 2)
        
        # Add text instructions
        cv2.putText(img, "Position barcode in green box", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, "Get close for macro focus", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

def iphone_macro_camera_interface():
    """Advanced camera interface optimized for iPhone macro mode (auto start/stop detection and stream)"""
    st.subheader("📱 iPhone Macro Camera")
    st.info("🔍 **Macro Mode Enabled**: This camera interface is optimized for iPhone macro photography")
    # Device-specific instructions
    col1, col2 = st.columns(2)
    with col1:
        st.write("**📱 iPhone Instructions:**")
        st.write("• Camera will auto-enable macro mode")
        st.write("• Get within 2-10cm of barcode")
        st.write("• Align barcode with green box")
        st.write("• Hold steady for auto-focus")
    with col2:
        st.write("**🎯 Positioning Tips:**")
        st.write("• Fill the green box with barcode")
        st.write("• Ensure good lighting")
        st.write("• Keep barcode flat and straight")
        st.write("• Wait for focus confirmation")
    # Camera constraints for different devices
    device_type = st.selectbox(
        "Select your device type:",
        ["iPhone (iOS 13+)", "Android", "Desktop/Other"],
        key="device_type"
    )
    if device_type == "iPhone (iOS 13+)":
        camera_constraints = get_iphone_camera_constraints()
    elif device_type == "Android":
        camera_constraints = get_android_camera_constraints()
    else:
        camera_constraints = {"video": True, "audio": False}
    # Initialize camera processor
    processor = MacroCameraProcessor()
    # WebRTC streamer with macro optimizations
    webrtc_ctx = webrtc_streamer(
        key="macro_barcode_scanner",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        ),
        video_processor_factory=lambda: processor,
        media_stream_constraints=camera_constraints,
        async_processing=True,
    )
    # Automatically enable detection when stream is active
    if webrtc_ctx.state.playing and webrtc_ctx.video_processor:
        webrtc_ctx.video_processor.detection_enabled = True
    # Check for barcode detection results
    if webrtc_ctx.video_processor:
        try:
            while not webrtc_ctx.video_processor.result_queue.empty():
                result = webrtc_ctx.video_processor.result_queue.get_nowait()
                st.success(f"✅ Barcode detected: {result['barcode']}")
                st.info(f"🔍 Detection method: {result['method']}")
                st.session_state['scanned_barcode'] = result['barcode']
                # Stop detection and stream after successful scan
                webrtc_ctx.video_processor.detection_enabled = False
                if hasattr(webrtc_ctx, 'stop'):
                    webrtc_ctx.stop()
                break
        except queue.Empty:
            pass
    # Fallback for devices that don't support advanced constraints
    if not webrtc_ctx.state.playing:
        st.warning("⚠️ **Camera not active.** If you're having issues:")
        st.write("• Allow camera permissions when prompted") 
        st.write("• Try refreshing the page")
    return None

st.set_page_config(page_title="Bike Inventory", layout="wide")
st.title("🚲 Bike Spare Parts Inventory")

# Initialize the database connection
@st.cache_resource
def get_db_connection():
    """
    Create a database connection that's properly cached and thread-safe.
    SQLAlchemy's connection pool will handle threading issues.
    """
    return InventoryDB()

# Create a database connection that's properly cached and shared between threads
db = get_db_connection()

# Initialize session state
if 'captured_image' not in st.session_state:
    st.session_state['captured_image'] = None
    
if 'scanned_barcode' not in st.session_state:
    st.session_state['scanned_barcode'] = None

# Create tabs
tab1, tab2 = st.tabs(["➕ Add New Item", "📋 Inventory List"])

with tab1:
    # Create two columns for camera inputs
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📷 Take Photo")
        
        # Use simplified camera input
        camera_photo = st.camera_input("Take a picture", key="photo_camera")
        if camera_photo is not None:
            # Convert the camera input to OpenCV format
            image = Image.open(camera_photo)
            img_array = np.array(image)
            st.session_state['captured_image'] = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            st.success("Photo captured successfully!")
        
        # File upload option as alternative
        st.info("📸 Or upload an image file:")
        uploaded_photo = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="photo_upload")
        if uploaded_photo is not None:
            # Convert the uploaded file to an image
            image = Image.open(uploaded_photo)
            img_array = np.array(image)
            st.session_state['captured_image'] = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            st.success("Photo uploaded successfully!")
        
        if st.session_state['captured_image'] is not None:
            st.image(st.session_state['captured_image'], caption="Captured Photo", channels="BGR")
            
    with col2:
        st.subheader("📊 Scan Barcode")
        # Only show live detection (iPhone Macro Camera)
        st.info("Live barcode detection with iPhone Macro Camera is enabled.")
        image_to_process = iphone_macro_camera_interface()
        # Process the image if we have one
        if image_to_process is not None:
            # Analyze image quality first
            with st.expander("📊 Image Quality Analysis", expanded=False):
                quality_info = analyze_image_quality(image_to_process)
                st.write(f"**Image size:** {quality_info['size']}")
                st.write(f"**Brightness:** {quality_info['mean_brightness']:.1f}")
                st.write(f"**Contrast:** {quality_info['contrast']}")
                st.write(f"**Sharpness:** {quality_info['sharpness']:.1f}")
                if quality_info['recommendations']:
                    st.warning("**Recommendations for better detection:**")
                    for rec in quality_info['recommendations']:
                        st.write(f"• {rec}")
                else:
                    st.success("📊 Image quality looks good for barcode detection!")
            # Use enhanced barcode detection
            st.info("🔍 Running enhanced barcode detection...")
            with st.spinner("Processing image with multiple detection methods..."):
                try:
                    barcodes, detection_method, _ = comprehensive_barcode_detection(image_to_process, debug=False)
                except Exception as e:
                    st.error(f"❌ Error during barcode detection: {str(e)}")
                    barcodes = []
                    detection_method = "Error occurred"
            # Convert image to display format
            img_array = np.array(image_to_process)
            if len(img_array.shape) == 3:
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = img_array
            st.image(img_bgr, caption="Image for Barcode Scan", channels="BGR", width=300)
            if barcodes:
                for barcode in barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    st.session_state['scanned_barcode'] = barcode_data
                    st.success(f"✅ {barcode_type} detected: {barcode_data}")
                    st.info(f"🔍 Detection method: {detection_method}")
                    if hasattr(barcode, 'rect'):
                        st.info(f"📍 Barcode location: x={barcode.rect.left}, y={barcode.rect.top}, "
                               f"width={barcode.rect.width}, height={barcode.rect.height}")
                    break  # Use the first barcode found
            else:
                st.error("❌ No barcode detected with any method.")
                try:
                    quality_info = analyze_image_quality(image_to_process)
                    st.warning("**🔍 Image Analysis Results:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**📊 Image Metrics:**")
                        st.write(f"• Size: {quality_info['size'][1]}×{quality_info['size'][0]} pixels")
                        st.write(f"• Brightness: {quality_info['mean_brightness']:.1f}/255")
                        st.write(f"• Contrast: {quality_info['contrast']}/255")
                        st.write(f"• Sharpness: {quality_info['sharpness']:.1f}")
                    with col2:
                        st.write("**💡 Recommendations:**")
                        if quality_info['recommendations']:
                            for rec in quality_info['recommendations']:
                                st.write(f"• {rec}")
                        else:
                            st.write("• Image quality appears adequate")
                            st.write("• Barcode may not be present or readable")
                            st.write("• Try a different image or manual entry")
                except Exception as e:
                    st.warning(f"Could not analyze image quality: {str(e)}")
                
                # Provide specific guidance for iPhone users
                if barcode_input_method == "📱 Upload Photo (Highest Quality)":
                    st.warning("**📱 iPhone Photography Tips:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**📸 Camera Settings:**")
                        st.write("• Enable macro mode if available")
                        st.write("• Tap to focus on the barcode")
                        st.write("• Use good lighting")
                        st.write("• Hold steady while focusing")
                    
                    with col2:
                        st.write("**🎯 Positioning:**")
                        st.write("• Fill frame with barcode")
                        st.write("• Keep barcode flat/straight")
                        st.write("• Avoid shadows and glare")
                        st.write("• Try different distances")
                else:
                    st.warning("**Try the following:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**📸 Camera technique:**")
                        st.write("• Hold camera steady")
                        st.write("• Ensure good focus")
                        st.write("• Fill frame with barcode")
                        st.write("• Try different distances")
                    
                    with col2:
                        st.write("**💡 Better option:**")
                        st.write("• Switch to 'Upload Photo'")
                        st.write("• Take photo with camera app")
                        st.write("• Use macro focus if available")
                        st.write("• Upload the saved photo")
                
                st.info("**📊 Supported formats:** QR codes, CODE128, CODE39, EAN13, UPC-A, DATA_MATRIX")
                st.warning("**Or enter the barcode manually below.**")
        
        # Manual barcode entry
        st.info("📊 Or enter the barcode manually:")
        manual_barcode = st.text_input("Enter barcode manually", key="manual_barcode")
        if manual_barcode and manual_barcode.strip():
            st.session_state['scanned_barcode'] = manual_barcode.strip()
            st.success(f"Barcode set manually: {st.session_state['scanned_barcode']}")
        
        if st.session_state['scanned_barcode']:
            st.success(f"Current barcode: {st.session_state['scanned_barcode']}")

    # Add item form
    st.subheader("Item Details")
    with st.form("add_item_form", clear_on_submit=True):
        name = st.text_input("Part Name", max_chars=100)
        
        # Use scanned barcode if available, or allow manual entry
        barcode_value = st.session_state.get('scanned_barcode', "")
        barcode = st.text_input("Barcode", value=barcode_value)
        
        # Add optional category and quantity fields
        category = st.selectbox("Category", ["Frame", "Wheels", "Drivetrain", "Brakes", "Controls", "Other"])
        quantity = st.number_input("Quantity", min_value=1, value=1)
        
        # Allow manual upload as a fallback
        manual_photo = st.file_uploader("Or upload a photo manually", type=["jpg", "jpeg", "png"], 
                                    accept_multiple_files=False, key="manual_photo")
        
        submitted = st.form_submit_button("Add Item")
        
        if submitted and name:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            image_path = None
            
            # Handle image saving
            if st.session_state['captured_image'] is not None:
                # Generate a unique filename
                image_filename = f"{uuid.uuid4()}.png"
                image_path = str(IMAGE_DIR / image_filename)
                
                # Convert CV2 image to PIL image and save to file
                img = Image.fromarray(cv2.cvtColor(st.session_state['captured_image'], cv2.COLOR_BGR2RGB))
                img.save(image_path)
                
            # Fallback to manually uploaded image
            elif manual_photo:
                # Generate a unique filename
                image_filename = f"{uuid.uuid4()}.png"
                image_path = str(IMAGE_DIR / image_filename)
                
                # Save the uploaded image to file
                img = Image.open(manual_photo)
                img.save(image_path)
            
            # Save to database
            db.add_part(
                name=name,
                barcode=barcode,
                category=category,
                quantity=quantity,
                image_path=image_path,
                timestamp=timestamp
            )
            
            # Reset captured data after adding to inventory
            st.session_state['captured_image'] = None
            st.session_state['scanned_barcode'] = None
            
            st.success(f"Added '{name}' to inventory.")

with tab2:
    # Add search, scan and filter functionality
    st.subheader("Search Inventory")
    
    # Create tabs for different search methods
    search_tab1, search_tab2 = st.tabs(["🔍 Text Search", "📊 Barcode Scan"])
    
    # Text search tab
    with search_tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            search_query = st.text_input("Search by name or barcode")
        
        with col2:
            category_filter = st.selectbox(
                "Filter by category",
                ["All Categories", "Frame", "Wheels", "Drivetrain", "Brakes", "Controls", "Other"],
                index=0
            )
    
    # Barcode scan tab
    with search_tab2:
        st.write("Scan a barcode to search the inventory")
        
        # Create a session state variable for inventory search
        if 'inventory_search_barcode' not in st.session_state:
            st.session_state['inventory_search_barcode'] = None
        
        # Provide multiple input methods for inventory search
        search_input_method = st.radio(
            "Choose search input method:",
            ["📱 Upload Barcode Photo", "📷 Use Camera"],
            key="search_input_method",
            help="For iPhone users: Use 'Upload Photo' for better macro focus"
        )
        
        search_image_to_process = None
        
        if search_input_method == "📱 Upload Barcode Photo":
            st.info("💡 **iPhone Users:** Take a focused photo with your camera app, then upload it here!")
            
            # File uploader for inventory search
            uploaded_search_barcode = st.file_uploader(
                "Upload barcode image for search", 
                type=["jpg", "jpeg", "png", "heic"],
                key="search_barcode_upload",
                help="Upload a clear photo of the barcode to search for in inventory"
            )
            
            if uploaded_search_barcode is not None:
                try:
                    search_image_to_process = Image.open(uploaded_search_barcode)
                    st.success("✅ Search image uploaded successfully!")
                except Exception as e:
                    st.error(f"❌ Error loading search image: {e}")
        
        else:  # Camera input for search
            st.warning("⚠️ **Note:** For small barcodes, consider using 'Upload Photo' for better focus.")
            
            inventory_barcode_camera = st.camera_input("Scan barcode to search inventory", key="inventory_barcode_camera")
            if inventory_barcode_camera is not None:
                search_image_to_process = Image.open(inventory_barcode_camera)
        
        # Process search image if available
        if search_image_to_process is not None:
            # Use enhanced barcode detection
            st.info("🔍 Searching for barcodes in image...")
            
            with st.spinner("Processing image with enhanced detection..."):
                barcodes, search_detection_method, _ = enhanced_barcode_detection(search_image_to_process, debug=False)
            
            # Convert image to display format
            img_array = np.array(search_image_to_process)
            if len(img_array.shape) == 3:
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = img_array
            
            # Display the captured image for debugging
            st.image(img_bgr, caption="Image for Barcode Search", channels="BGR", width=300)
            
            if barcodes:
                for barcode in barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type
                    st.session_state['inventory_search_barcode'] = barcode_data
                    st.success(f"✅ {barcode_type} detected: {barcode_data}")
                    st.info(f"🔍 Detection method: {search_detection_method}")
                    break  # Use the first barcode found
            else:
                st.error("❌ No barcode detected with enhanced detection.")
                if search_input_method == "📱 Upload Barcode Photo":
                    st.warning("**📱 Try these iPhone photography tips:**")
                    st.write("• Enable macro mode for small barcodes")
                    st.write("• Tap to focus directly on the barcode")
                    st.write("• Ensure bright, even lighting")
                    st.write("• Fill the frame with the barcode")
                else:
                    st.warning("**Try switching to 'Upload Photo' for better results with small barcodes.**")
        
        # Display detected barcode
        if st.session_state['inventory_search_barcode']:
            st.success(f"Searching for barcode: {st.session_state['inventory_search_barcode']}")
            
            # Use the scanned barcode for search
            search_query = st.session_state['inventory_search_barcode']
            
            # Add a button to clear the search
            if st.button("Clear Barcode Search"):
                st.session_state['inventory_search_barcode'] = None
                search_query = ""
                st.rerun()
        else:
            # If no barcode is scanned, don't override the text search
            search_query = search_query

    # Get inventory from database with search filters
    filtered_inventory = db.search_parts(
        query=search_query if search_query else None,
        category=category_filter if category_filter != "All Categories" else None
    )
    
    # Get total count (all items)
    all_inventory = db.get_all_parts()
    
    # Display total count
    st.write(f"Showing {len(filtered_inventory)} of {len(all_inventory)} items")
    
    # Display inventory in a more organized layout
    if filtered_inventory:
        col1, col2, col3 = st.columns(3)
        
        for idx, item in enumerate(filtered_inventory):
            # Distribute items across columns
            with [col1, col2, col3][idx % 3]:
                with st.container():
                    st.subheader(f"{item['name']}")
                    if item['image_path'] and os.path.exists(item['image_path']):
                        st.image(item['image_path'], width=200)
                    st.write(f"📊 Barcode: {item['barcode'] or 'N/A'}")
                    if 'category' in item:
                        st.write(f"🏷️ Category: {item['category']}")
                    if 'quantity' in item:
                        st.write(f"🔢 Quantity: {item['quantity']}")
                    st.write(f"⏱️ Added: {item.get('timestamp', 'N/A')}")
                    
                    # Actions row
                    col_edit, col_delete = st.columns(2)
                    
                    with col_edit:
                        if st.button(f"Edit", key=f"edit_{idx}"):
                            st.session_state['editing_item'] = item
                            st.session_state['editing_index'] = item['id']
                    
                    with col_delete:
                        if st.button(f"Delete", key=f"delete_{idx}"):
                            # Delete image file if it exists
                            image_path = db.delete_part(item['id'])
                            if image_path and os.path.exists(image_path):
                                os.remove(image_path)
                            st.rerun()
                            
                    st.markdown("---")
                    
        # Item editing modal (simple implementation)
        if 'editing_item' in st.session_state and st.session_state['editing_item']:
            with st.expander("Edit Item", expanded=True):
                edit_item = st.session_state['editing_item']
                edit_id = st.session_state['editing_index']
                
                edited_name = st.text_input("Name", value=edit_item['name'])
                edited_barcode = st.text_input("Barcode", value=edit_item['barcode'] or "")
                
                # Get category index safely
                category_options = ["Frame", "Wheels", "Drivetrain", "Brakes", "Controls", "Other"]
                try:
                    category_index = category_options.index(edit_item.get('category', 'Other'))
                except ValueError:
                    category_index = category_options.index('Other')
                
                edited_category = st.selectbox(
                    "Category", 
                    category_options,
                    index=category_index
                )
                edited_quantity = st.number_input("Quantity", value=int(edit_item.get('quantity', 1)), min_value=1)
                
                # Option to replace the image
                new_photo = st.file_uploader("Replace photo", type=["jpg", "jpeg", "png"], key="edit_photo")
                
                if st.button("Save Changes"):
                    image_path = edit_item.get('image_path')
                    
                    # Handle new image if uploaded
                    if new_photo:
                        # Remove old image if it exists
                        if image_path and os.path.exists(image_path):
                            try:
                                os.remove(image_path)
                            except:
                                pass
                            
                        # Save new image
                        image_filename = f"{uuid.uuid4()}.png"
                        image_path = str(IMAGE_DIR / image_filename)
                        img = Image.open(new_photo)
                        img.save(image_path)
                    
                    # Update the database
                    db.update_part(
                        part_id=edit_id,
                        name=edited_name,
                        barcode=edited_barcode,
                        category=edited_category,
                        quantity=edited_quantity,
                        image_path=image_path if new_photo else None
                    )
                    
                    # Clear editing state
                    st.session_state['editing_item'] = None
                    st.session_state['editing_index'] = None
                    st.rerun()
                    
                if st.button("Cancel"):
                    st.session_state['editing_item'] = None
                    st.session_state['editing_index'] = None
                    st.rerun()
    else:
        st.info("No items match your search criteria. Try a different search or filter.")

# Sidebar with instructions and settings
st.sidebar.title("Instructions")
st.sidebar.markdown("""
### How to use this app:
1. **Navigate between tabs** using the tabs at the top:
   - "Add New Item" to add parts to your inventory
   - "Inventory List" to view and manage your items

2. **Adding new items**:
   - Allow camera access when prompted
   - Capture a photo of the part
   - Scan a barcode if available
   - Fill in the part details and click "Add Item"

3. **Managing inventory**:
   - Search by name or barcode
   - Filter by category
   - Edit or delete items as needed

Works best on mobile devices with camera access.
""")

# Export/Import functionality
st.sidebar.title("Data Management")

# Export data
if st.sidebar.button("Export Inventory Data"):
    # Convert the inventory data to JSON
    import json
    import base64
    import shutil
    
    inventory_items = db.get_all_parts()
    if inventory_items:
        # Create a temporary folder for export with images
        export_folder = Path(tempfile.mkdtemp())
        export_images_folder = export_folder / "images"
        export_images_folder.mkdir(exist_ok=True)
        
        # Process each item
        export_data = []
        for item in inventory_items:
            export_item = dict(item)
            
            # Handle the image
            if item.get('image_path') and os.path.exists(item['image_path']):
                # Copy the image to the export folder
                image_name = os.path.basename(item['image_path'])
                export_image_path = str(export_images_folder / image_name)
                shutil.copy2(item['image_path'], export_image_path)
                
                # Update the path to be relative
                export_item['image_relative_path'] = f"images/{image_name}"
            
            # Remove absolute path as it won't be valid when imported elsewhere
            if 'image_path' in export_item:
                del export_item['image_path']
                
            export_data.append(export_item)
            
        # Save the data as JSON
        export_json_path = export_folder / "inventory_data.json"
        with open(export_json_path, 'w') as f:
            json.dump(export_data, f)
            
        # Create a ZIP file
        import zipfile
        zip_path = os.path.join(tempfile.gettempdir(), "bike_inventory_export.zip") 
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add the JSON file
            zipf.write(export_json_path, arcname="inventory_data.json")
            
            # Add all images
            for img_file in export_images_folder.glob("*"):
                zipf.write(img_file, arcname=f"images/{img_file.name}")
        
        # Read the ZIP file and create download link
        with open(zip_path, 'rb') as f:
            zip_bytes = f.read()
            
        b64 = base64.b64encode(zip_bytes).decode()
        href = f'<a href="data:application/zip;base64,{b64}" download="bike_inventory_export.zip">Download Inventory Export (ZIP)</a>'
        st.sidebar.markdown(href, unsafe_allow_html=True)
        
        # Clean up temp files
        shutil.rmtree(export_folder)
        os.remove(zip_path)
    else:
        st.sidebar.warning("No inventory data to export.")

# Import data
st.sidebar.subheader("Import Data")
uploaded_file = st.sidebar.file_uploader("Upload Inventory ZIP Export", type=['zip'])
if uploaded_file is not None:
    try:
        import zipfile
        import json
        import tempfile
        import shutil
        
        # Create temp directory to extract files
        extract_dir = Path(tempfile.mkdtemp())
        
        # Save uploaded file to temp location
        zip_path = os.path.join(extract_dir, "upload.zip")
        with open(zip_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Extract the ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Load the JSON data
        json_path = extract_dir / "inventory_data.json"
        with open(json_path, 'r') as f:
            import_data = json.load(f)
        
        # Process each item
        imported_count = 0
        for item in import_data:
            # Handle image if it exists
            image_path = None
            if 'image_relative_path' in item:
                source_image = extract_dir / item['image_relative_path']
                if source_image.exists():
                    # Copy to our images folder
                    dest_filename = f"{uuid.uuid4()}{source_image.suffix}"
                    dest_path = IMAGE_DIR / dest_filename
                    shutil.copy2(source_image, dest_path)
                    image_path = str(dest_path)
                del item['image_relative_path']
            
            # Add to database (skip ID if present)
            if 'id' in item:
                del item['id']
                
            # Check if item exists (by name and barcode)
            existing_items = db.search_parts(
                query=item['name']
            )
            
            existing_match = False
            for existing in existing_items:
                if existing['name'] == item['name'] and existing['barcode'] == item['barcode']:
                    existing_match = True
                    break
                
            if not existing_match:
                # Add the item to database
                db.add_part(
                    name=item['name'],
                    barcode=item.get('barcode', ''),
                    category=item.get('category', 'Other'),
                    quantity=item.get('quantity', 1),
                    image_path=image_path,
                    timestamp=item.get('timestamp')
                )
                imported_count += 1
        
        # Clean up temp directory
        shutil.rmtree(extract_dir)
        
        st.sidebar.success(f"Successfully imported {imported_count} new items!")
    except Exception as e:
        st.sidebar.error(f"Error importing data: {str(e)}")

# Clear all data button (with confirmation)
st.sidebar.subheader("Clear Data")
if st.sidebar.button("Clear All Inventory Data"):
    st.sidebar.warning("Are you sure? This cannot be undone.")
    confirm_col1, confirm_col2 = st.sidebar.columns(2)
    with confirm_col1:
        if st.button("✅ Yes, Clear All"):
            # Get all items to delete their images
            all_items = db.get_all_parts()
            
            # Delete all image files
            for item in all_items:
                if item.get('image_path') and os.path.exists(item['image_path']):
                    try:
                        os.remove(item['image_path'])
                    except:
                        pass
            
            # Reset the database by recreating the table
            from sqlalchemy import inspect
            from db import Base
            
            # Drop all tables and recreate
            Base.metadata.drop_all(db.engine)
            Base.metadata.create_all(db.engine)
            
            st.rerun()
    with confirm_col2:
        if st.button("❌ Cancel"):
            pass

# iPhone Macro Camera Configuration
def get_iphone_camera_constraints():
    """Return camera constraints for iPhone macro mode."""
    # iPhone macro mode: high resolution, environment camera, no audio
    return {
        "video": {
            "width": {"min": 640, "ideal": 1920, "max": 4032},
            "height": {"min": 480, "ideal": 1440, "max": 3024},
            "facingMode": {"exact": "environment"},
            "focusMode": "continuous",
            "aspectRatio": {"ideal": 4/3},
            "frameRate": {"ideal": 30, "max": 60},
            # iPhone macro: get as close as possible
        },
        "audio": False
    }
