# Bike Inventory Setup Guide

This guide covers more advanced setup options and configurations for the Bike Inventory app.

## Deployment Options

### Running on a Server
To make the app accessible from other devices on your network:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### Running as a Service
To run the app as a background service on Linux, create a systemd service:

1. Create a service file `/etc/systemd/system/bike-inventory.service`:
```
[Unit]
Description=Bike Inventory App
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/bike-inventory
ExecStart=/usr/local/bin/streamlit run app.py --server.address 0.0.0.0
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

2. Enable and start the service:
```bash
sudo systemctl enable bike-inventory
sudo systemctl start bike-inventory
```

## Database Management

### Backup Database
To manually backup the SQLite database:

```bash
cp bike_inventory.db bike_inventory_backup_$(date +%Y%m%d).db
```

### Database Optimization
To optimize the database performance:

```bash
sqlite3 bike_inventory.db "VACUUM;"
```

### SQLAlchemy Configuration
The app uses SQLAlchemy with the following thread-safe configuration:

```python
engine = create_engine(
    f"sqlite:///{db_path}", 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)
```

This configuration ensures:
- `check_same_thread=False`: Allows SQLite connections to be used across threads
- `poolclass=StaticPool`: Uses a single connection that's shared across threads
- `scoped_session`: Creates thread-local sessions to prevent concurrency issues

## Advanced Customization

### Adding Custom Fields
To add custom fields to the inventory items:

1. Update the database schema in `db.py`:
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
    custom_field_1 = Column(String)  # Add your custom field here
    custom_field_2 = Column(String)  # Add another custom field here
```

2. Update the `add_part` and `update_part` methods to include the new fields

3. Add the fields to the UI in `app.py`

### Customizing the Camera Settings
To adjust camera resolution or behavior, modify the WebRTC configuration in `app.py`:

```python
media_stream_constraints = {
    "video": {
        "width": {"ideal": 1280},
        "height": {"ideal": 720},
        "frameRate": {"ideal": 30}
    },
    "audio": False
}
```

### Security Considerations

For production deployment:
- Set up HTTPS using a reverse proxy like Nginx
- Add authentication
- Store the SQLite database in a location not accessible via the web server

## Troubleshooting

### Camera issues
- If camera access fails, ensure your browser has permission to access the camera
- On some devices, you may need to use HTTPS for camera access
- Try different browsers (Safari works best on iOS)

### Database errors
- If the app fails to start due to database errors, check file permissions
- Make sure the user running the app has write access to the database file

### Image storage issues
- Check that the `static/images` directory exists and is writable
- Monitor disk space to ensure you don't run out when storing many images
