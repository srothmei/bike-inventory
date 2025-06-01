import os
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, select, insert, update, delete, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

Base = declarative_base()

class Part(Base):
    """SQLAlchemy ORM model for a bike part"""
    __tablename__ = 'parts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    barcode = Column(String)
    category = Column(String)
    quantity = Column(Integer, default=1)
    image_path = Column(String)
    timestamp = Column(String)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'barcode': self.barcode,
            'category': self.category,
            'quantity': self.quantity,
            'image_path': self.image_path,
            'timestamp': self.timestamp
        }

class InventoryDB:
    def __init__(self, db_path="bike_inventory.db"):
        """Initialize the SQLAlchemy engine and session"""
        self.db_path = db_path
        # Use connect_args with check_same_thread=False to avoid threading issues
        # Use StaticPool to ensure connections are reused across threads
        self.engine = create_engine(
            f"sqlite:///{db_path}", 
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
        
        # Create session factory
        self.session_factory = sessionmaker(bind=self.engine)
        # Use scoped_session to handle sessions per thread
        self.Session = scoped_session(self.session_factory)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        
    def close(self):
        """Close all sessions and dispose of the engine"""
        self.Session.remove()
        self.engine.dispose()
            
    def create_tables(self):
        """Create tables if they don't exist"""
        Base.metadata.create_all(self.engine)
        
    def add_part(self, name, barcode="", category="Other", quantity=1, image_path=None, timestamp=None):
        """Add a new part to the inventory"""
        session = self.Session()
        try:
            # Create new Part object
            new_part = Part(
                name=name,
                barcode=barcode,
                category=category,
                quantity=quantity,
                image_path=image_path,
                timestamp=timestamp
            )
            
            # Add to session and commit
            session.add(new_part)
            session.commit()
            
            # Get the ID of the new part
            part_id = new_part.id
            
            return part_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
    def get_all_parts(self):
        """Return all parts in the inventory"""
        session = self.Session()
        try:
            # Query all parts
            parts = session.query(Part).all()
            
            # Convert to dictionaries
            return [part.to_dict() for part in parts]
        finally:
            session.close()
        
    def search_parts(self, query=None, category=None):
        """Search parts by name, barcode, and/or category"""
        session = self.Session()
        try:
            # Start with base query
            parts_query = session.query(Part)
            
            # Add filters
            if query:
                parts_query = parts_query.filter(
                    (Part.name.like(f'%{query}%')) | 
                    (Part.barcode.like(f'%{query}%'))
                )
                
            if category and category != "All Categories":
                parts_query = parts_query.filter(Part.category == category)
                
            # Execute query
            parts = parts_query.all()
            
            # Convert to dictionaries
            return [part.to_dict() for part in parts]
        finally:
            session.close()
        
    def get_part(self, part_id):
        """Get a single part by ID"""
        session = self.Session()
        try:
            part = session.query(Part).filter(Part.id == part_id).first()
            if part:
                return part.to_dict()
            return None
        finally:
            session.close()
        
    def update_part(self, part_id, name, barcode, category, quantity, image_path=None):
        """Update an existing part"""
        session = self.Session()
        try:
            # Get the part
            part = session.query(Part).filter(Part.id == part_id).first()
            
            if part:
                # Update fields
                part.name = name
                part.barcode = barcode
                part.category = category
                part.quantity = quantity
                
                # Only update image path if provided
                if image_path:
                    part.image_path = image_path
                    
                # Commit changes
                session.commit()
                return True
            
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
    def delete_part(self, part_id):
        """Delete a part from the inventory"""
        session = self.Session()
        try:
            # Get the part first to retrieve image path
            part = session.query(Part).filter(Part.id == part_id).first()
            
            image_path = None
            if part:
                # Save the image path
                image_path = part.image_path
                
                # Delete the part
                session.delete(part)
                session.commit()
            
            # Return the image path if it exists
            return image_path
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
