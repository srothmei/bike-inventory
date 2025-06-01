# 🚲 Bike Spare Parts Inventory Manager

A mobile-friendly web application for managing your bicycle spare parts inventory with barcode scanning and photo capture capabilities. Uses SQLite for persistent storage and saves images to the filesystem.

## 📋 Table of Contents
- [🚀 Features](#-features)
- [📦 Requirements](#-requirements)
- [📁 Project Structure](#-project-structure)
- [💿 Installation](#-installation)
  - [Local Installation](#local-installation)
  - [Docker Installation](#docker-installation)
- [👩‍💻 Usage](#-usage)
  - [Adding Items](#adding-items-tab-1)
  - [Managing Inventory](#managing-inventory-tab-2)
  - [Data Management](#data-management)
- [🔧 Technical Implementation](#-technical-implementation)
  - [Database Structure](#database-structure)
  - [Image Storage](#image-storage)
  - [Import/Export Format](#importexport-format)
- [📱 Notes for iOS Users](#-notes-for-ios-users)
- [🛠️ Customization](#️-customization)
- [📜 License](#-license)

## 🚀 Features

- Add spare parts to your inventory with names, barcodes, and photos
- Scan barcodes directly from the browser using your device camera
- Take photos of items using your device camera
- Search inventory by name, text input, or direct barcode scanning
- Filter items by category (Frame, Wheels, Drivetrain, Brakes, Controls, Other)
- Track quantity of each part
- Edit existing items
- Mobile-friendly tabbed interface designed for iOS and other devices
- Persistent storage with SQLite database
- File-based image storage for better performance and reliability
- Export/Import functionality with ZIP files to backup your inventory

## 📦 Requirements

- Python 3.x
- Streamlit
- SQLAlchemy (with SQLite)
- OpenCV
- pyzbar (barcode detection)
- Pillow (image processing)
- streamlit-webrtc (camera access)

## 📁 Project Structure

```
bike-inventory/
├── app.py                # Main Streamlit application
├── db.py                 # SQLite database management module
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── bike_inventory.db     # SQLite database file (created on first run)
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Docker Compose configuration for local deployment
├── docker-compose.prod.yml # Production-ready Docker Compose configuration
├── docker-compose.secure.yml # HTTPS-enabled Docker Compose configuration
├── docker-compose.override.yml # Development configuration
├── .env.example          # Environment variables example file
├── entrypoint.sh         # Container initialization script
├── healthcheck.sh        # Container health monitoring
├── bike-inventory.sh     # Management script for deployment
├── update.sh             # Update script for keeping app current
├── Documentation/
│   ├── DOCKER_DEPLOYMENT.md  # Docker deployment instructions
│   ├── HTTPS_DEPLOYMENT.md   # HTTPS deployment guide
│   ├── MOBILE_ACCESS.md      # Mobile device access instructions
│   ├── DEVELOPERS.md         # Guide for developers
│   └── DOCKER_ENHANCEMENTS.md # Docker enhancement details
├── nginx/                # Nginx configurations for HTTPS
│   ├── bike-inventory.conf # Nginx site configuration
│   └── ssl/              # SSL certificates directory
└── static/               # Static files directory
    └── images/           # Stored photos of inventory items
```
```

## 💿 Installation

### Local Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

### 🐳 Docker Installation

For deployment on a local network server, you can use Docker:

1. Clone this repository
2. Build and start the container:
   ```bash
   docker-compose up -d
   ```
3. Access the application at `http://SERVER_IP:8501`

We provide several deployment options:
- **🔹 Basic deployment**: Use docker-compose.yml for simple setups
- **🔷 Production deployment**: Use docker-compose.prod.yml for better stability
- **🔒 Secure deployment**: Use docker-compose.secure.yml for HTTPS support

For detailed Docker deployment instructions, see:
- [🐳 Docker Deployment Guide](DOCKER_DEPLOYMENT.md)
- [🔒 HTTPS Deployment Guide](HTTPS_DEPLOYMENT.md)
- [📱 Mobile Access Guide](MOBILE_ACCESS.md)

## 👩‍💻 Usage

### Adding Items (Tab 1)
1. Navigate to the "Add New Item" tab
2. Allow camera access when prompted
3. To add a new part:
   - Take a photo by clicking "START" under "Take Photo" and then "Capture Photo"
   - Scan a barcode by clicking "START" under "Scan Barcode" and pointing your camera at a barcode
   - Fill in the part details (name, category, quantity)
   - Click "Add Item"

### Managing Inventory (Tab 2)
1. Navigate to the "Inventory List" tab
2. Search for items using one of two methods:
   - **🔍 Text Search**: Type in the search box to find items by name or barcode
   - **📷 Barcode Scan**: Use your device camera to scan a barcode directly
3. Filter items by category using the dropdown
4. For each item you can:
   - 👁️ View item details and photo
   - ✏️ Edit the item information with the "Edit" button
   - 🗑️ Delete the item with the "Delete" button

### Data Management
1. Use the sidebar for data management options:
   - 📤 Export your inventory as a ZIP file containing all data and images
   - 📥 Import previously exported inventory data
   - 🧹 Clear all inventory data (with confirmation)

## 🔧 Technical Implementation

### Database Structure
The application uses SQLAlchemy with SQLite for thread-safe persistent storage. The schema is defined using SQLAlchemy ORM:

```python
class Part(Base):
    __tablename__ = 'parts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    barcode = Column(String)
    category = Column(String)
    quantity = Column(Integer, default=1)
    image_path = Column(String)
    timestamp = Column(String)
```

SQLAlchemy provides thread safety to prevent the common SQLite error: "SQLite objects created in a thread can only be used in that same thread".

### Image Storage
Photos are stored in the file system:
- 📂 Location: `/static/images/` directory
- 🏷️ File naming: UUID-based to prevent conflicts (e.g., `3e4a8f2b-d5c6-4a2d-9b7e-8f1a2b3c4d5e.png`)
- 🔗 Images are referenced in the database by their file paths

### Import/Export Format
The export function creates a ZIP file containing:
- 📄 `inventory_data.json`: All inventory data
- 🖼️ `images/`: Folder containing all the photos

## 📱 Notes for iOS Users

For the best experience on iOS:
- 🧭 Use Safari browser
- 🔐 Grant camera permissions when prompted
- 📊 For barcode scanning, hold the barcode steady in front of the camera
- 📤 If the camera doesn't work, you can still manually upload photos
- 🔄 Works best in landscape mode for the tabbed interface

## 🛠️ Customization

- 🔖 Add new categories: Modify the category options list in `app.py`
- 💾 Change database location: Modify the `db_path` parameter in the `InventoryDB` class
- 🖼️ Change image storage location: Update the `IMAGE_DIR` variable in `app.py`

## 📜 License

[MIT License](LICENSE)
