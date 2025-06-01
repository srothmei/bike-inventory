# 👩‍💻 Bike Inventory Developer Guide

This guide is intended for developers who want to extend or modify the Bike Inventory application.

## 📋 Table of Contents
- [🛠️ Development Setup](#️-development-setup)
  - [Local Development](#local-development)
  - [Docker Development](#docker-development)
- [📁 Project Structure](#-project-structure)
- [💾 Database Schema](#-database-schema)
- [✨ Adding New Features](#-adding-new-features)
  - [New Fields for Parts](#new-fields-for-parts)
  - [New Categories](#new-categories)
  - [Custom Styling](#custom-styling)
- [🧪 Testing](#-testing)
- [🚀 Building for Production](#-building-for-production)
- [🤝 Contribution Guidelines](#-contribution-guidelines)
- [📜 License](#-license)

## Development Setup

### Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application in development mode:
   ```bash
   streamlit run app.py
   ```

### Docker Development

For development using Docker:

1. Use the development override:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.override.yml up
   ```

This will:
- Mount your local code directory into the container
- Enable auto-reload when files change
- Enable debugging features

## Project Structure

- `app.py`: Main Streamlit application
- `db.py`: Database management using SQLAlchemy
- `config.py`: Configuration management
- Docker files:
  - `Dockerfile`: Container definition
  - `docker-compose.yml`: Basic deployment
  - `docker-compose.prod.yml`: Production deployment
  - `docker-compose.secure.yml`: HTTPS-enabled deployment
  - `docker-compose.override.yml`: Development settings
- Scripts:
  - `entrypoint.sh`: Container initialization
  - `healthcheck.sh`: Container health monitoring
  - `generate_ssl_cert.sh`: SSL certificate generation
  - `bike-inventory.sh`: Management script

## Database Schema

The application uses SQLite with SQLAlchemy ORM. The schema is defined in `db.py`:

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

## Adding New Features

### New Fields for Parts

To add new fields to parts:

1. Update the `Part` class in `db.py`
2. Add form fields in `app.py`
3. Update the display logic in the inventory list

### New Categories

To add new categories:

1. Update the `get_categories()` method in `config.py`

### Custom Styling

To customize the look and feel:

1. Use Streamlit's built-in theming by creating a `.streamlit/config.toml` file
2. Add custom CSS using `st.markdown` with HTML/CSS

## Testing

You can run tests using:

```bash
pytest tests/
```

## Building for Production

To build for production:

1. Update the version in `app.py`
2. Update the `CHANGELOG.md`
3. Build using:
   ```bash
   ./bike-inventory.sh rebuild
   ```
4. Deploy using:
   ```bash
   ./bike-inventory.sh start-prod
   ```

## Contribution Guidelines

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Write tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
