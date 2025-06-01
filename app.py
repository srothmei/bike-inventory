import streamlit as st
import cv2
from PIL import Image
import io
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import tempfile
import time
import os
import uuid
from pathlib import Path
from pyzbar.pyzbar import decode
from db import InventoryDB
from config import Config

# Initialize directory structure
Config.init_dirs()

# Use config for file paths
STATIC_DIR = Config.STATIC_DIR
IMAGE_DIR = Config.IMAGE_DIR

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

# RTC configuration for WebRTC (needed for some networks)
rtc_configuration = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# Create tabs
tab1, tab2 = st.tabs(["➕ Add New Item", "📋 Inventory List"])

with tab1:
    # Create two columns for camera inputs
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📷 Take Photo")
        
        def video_frame_callback(frame):
            img = frame.to_ndarray(format="bgr24")
            return img

        ctx = webrtc_streamer(
            key="photo_capture",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc_configuration,
            video_frame_callback=video_frame_callback,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
        
        if st.button("Capture Photo"):
            if ctx.video_transformer:
                if ctx.state.playing:
                    # Get frame from the video stream
                    frame = ctx.video_receiver.get_frame()
                    if frame is not None:
                        img = frame.to_ndarray(format="bgr24")
                        st.session_state['captured_image'] = img
                        st.success("Photo captured!")
                else:
                    st.warning("Please start the camera by clicking 'START' first.")
            else:
                st.warning("Camera is not available. Please allow camera access.")
        
        if st.session_state['captured_image'] is not None:
            st.image(st.session_state['captured_image'], caption="Captured Photo", channels="BGR")
            
    with col2:
        st.subheader("📊 Scan Barcode")
        
        def barcode_scanner(frame):
            img = frame.to_ndarray(format="bgr24")
            barcodes = decode(img)
            
            # Process detected barcodes
            for barcode in barcodes:
                # Extract barcode info
                barcode_data = barcode.data.decode('utf-8')
                barcode_type = barcode.type
                
                # Draw rectangle around barcode
                pts = np.array([barcode.polygon], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(img, [pts], True, (0, 255, 0), 2)
                
                # Put text with barcode data
                cv2.putText(img, barcode_data, (barcode.rect.left, barcode.rect.top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Store the most recent barcode
                st.session_state['scanned_barcode'] = barcode_data
            
            return img
        
        barcode_ctx = webrtc_streamer(
            key="barcode_scanner",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc_configuration,
            video_frame_callback=barcode_scanner,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
        
        if st.session_state['scanned_barcode']:
            st.success(f"Barcode detected: {st.session_state['scanned_barcode']}")

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
        
        # Barcode scanner function
        def inventory_barcode_scanner(frame):
            img = frame.to_ndarray(format="bgr24")
            barcodes = decode(img)
            
            # Process detected barcodes
            for barcode in barcodes:
                # Extract barcode info
                barcode_data = barcode.data.decode('utf-8')
                
                # Draw rectangle around barcode
                pts = np.array([barcode.polygon], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(img, [pts], True, (0, 255, 0), 2)
                
                # Put text with barcode data
                cv2.putText(img, barcode_data, (barcode.rect.left, barcode.rect.top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Store the most recent barcode for inventory search
                st.session_state['inventory_search_barcode'] = barcode_data
            
            return img
        
        # WebRTC streamer for inventory barcode scanning
        inventory_barcode_ctx = webrtc_streamer(
            key="inventory_barcode_scanner",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc_configuration,
            video_frame_callback=inventory_barcode_scanner,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
        
        # Display detected barcode
        if st.session_state['inventory_search_barcode']:
            st.success(f"Barcode detected: {st.session_state['inventory_search_barcode']}")
            
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
