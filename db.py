import sqlite3
import os
from pathlib import Path

class InventoryDB:
    def __init__(self, db_path="bike_inventory.db"):
        """Initialize the database connection"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        
    def connect(self):
        """Establish a database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.conn.cursor()
        
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        # Create parts table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            barcode TEXT,
            category TEXT,
            quantity INTEGER DEFAULT 1,
            image_path TEXT,
            timestamp TEXT
        )
        ''')
        self.conn.commit()
        
    def add_part(self, name, barcode="", category="Other", quantity=1, image_path=None, timestamp=None):
        """Add a new part to the inventory"""
        self.cursor.execute('''
        INSERT INTO parts (name, barcode, category, quantity, image_path, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, barcode, category, quantity, image_path, timestamp))
        self.conn.commit()
        return self.cursor.lastrowid
        
    def get_all_parts(self):
        """Return all parts in the inventory"""
        self.cursor.execute('SELECT * FROM parts')
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
        
    def search_parts(self, query=None, category=None):
        """Search parts by name, barcode, and/or category"""
        sql = 'SELECT * FROM parts WHERE 1=1'
        params = []
        
        if query:
            sql += ' AND (name LIKE ? OR barcode LIKE ?)'
            params.extend([f'%{query}%', f'%{query}%'])
            
        if category and category != "All Categories":
            sql += ' AND category = ?'
            params.append(category)
            
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]
        
    def get_part(self, part_id):
        """Get a single part by ID"""
        self.cursor.execute('SELECT * FROM parts WHERE id = ?', (part_id,))
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        return None
        
    def update_part(self, part_id, name, barcode, category, quantity, image_path=None):
        """Update an existing part"""
        if image_path:
            self.cursor.execute('''
            UPDATE parts
            SET name = ?, barcode = ?, category = ?, quantity = ?, image_path = ?
            WHERE id = ?
            ''', (name, barcode, category, quantity, image_path, part_id))
        else:
            self.cursor.execute('''
            UPDATE parts
            SET name = ?, barcode = ?, category = ?, quantity = ?
            WHERE id = ?
            ''', (name, barcode, category, quantity, part_id))
        self.conn.commit()
        return self.cursor.rowcount > 0
        
    def delete_part(self, part_id):
        """Delete a part from the inventory"""
        # First get the image path
        self.cursor.execute('SELECT image_path FROM parts WHERE id = ?', (part_id,))
        row = self.cursor.fetchone()
        
        # Delete the record
        self.cursor.execute('DELETE FROM parts WHERE id = ?', (part_id,))
        self.conn.commit()
        
        # Return the image path if it exists so we can delete the file
        if row and row['image_path']:
            return row['image_path']
        return None
