import sqlite3
import json
from datetime import datetime
from config import DATABASE_PATH
import os

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Clothes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clothes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                category TEXT,
                description TEXT,
                photo_file_id TEXT,
                photo_path TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Outfits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outfits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                description TEXT,
                clothes_ids TEXT,
                season TEXT,
                occasion TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                style_preference TEXT,
                color_preference TEXT,
                season_preference TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username=None, first_name=None, last_name=None):
        """Add or update user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        
        conn.commit()
        conn.close()
    
    def add_clothing_item(self, user_id, name, category, description, photo_file_id=None, photo_path=None, tags=None):
        """Add a clothing item to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_json = json.dumps(tags) if tags else None
        
        cursor.execute('''
            INSERT INTO clothes (user_id, name, category, description, photo_file_id, photo_path, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, category, description, photo_file_id, photo_path, tags_json))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return item_id
    
    def delete_clothing_item(self, user_id, item_id):
        """Delete a clothing item by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First check if the item exists and belongs to the user
        cursor.execute('''
            SELECT name, photo_path FROM clothes 
            WHERE id = ? AND user_id = ?
        ''', (item_id, user_id))
        
        item = cursor.fetchone()
        if not item:
            conn.close()
            return False, "Item not found or doesn't belong to you"
        
        # Delete the item
        cursor.execute('''
            DELETE FROM clothes 
            WHERE id = ? AND user_id = ?
        ''', (item_id, user_id))
        
        conn.commit()
        conn.close()
        
        # Delete photo file if it exists
        photo_path = item[1]
        if photo_path and os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except:
                pass  # Ignore errors if file deletion fails
        
        return True, f"Successfully deleted '{item[0]}'"
    
    def get_user_clothes(self, user_id, category=None):
        """Get all clothes for a user, optionally filtered by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT * FROM clothes 
                WHERE user_id = ? AND category = ?
                ORDER BY created_at DESC
            ''', (user_id, category))
        else:
            cursor.execute('''
                SELECT * FROM clothes 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
        
        clothes = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries with proper field names
        clothes_list = []
        for item in clothes:
            clothes_list.append({
                'id': item[0],
                'user_id': item[1],
                'name': item[2],
                'category': item[3],
                'description': item[4],
                'photo_file_id': item[5],
                'photo_path': item[6],
                'tags': json.loads(item[7]) if item[7] else [],
                'created_at': item[8]
            })
        
        return clothes_list
    
    def get_clothing_item(self, user_id, item_id):
        """Get a specific clothing item by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM clothes 
            WHERE id = ? AND user_id = ?
        ''', (item_id, user_id))
        
        item = cursor.fetchone()
        conn.close()
        
        if item:
            return {
                'id': item[0],
                'user_id': item[1],
                'name': item[2],
                'category': item[3],
                'description': item[4],
                'photo_file_id': item[5],
                'photo_path': item[6],
                'tags': json.loads(item[7]) if item[7] else [],
                'created_at': item[8]
            }
        return None
    
    def update_clothing_item(self, user_id, item_id, field, value):
        """Update a specific field of a clothing item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if item exists and belongs to user
        cursor.execute('''
            SELECT id FROM clothes 
            WHERE id = ? AND user_id = ?
        ''', (item_id, user_id))
        
        if not cursor.fetchone():
            conn.close()
            return False
        
        # Handle different field types
        if field == "tags":
            value = json.dumps(value)
        
        # Update the field
        cursor.execute(f'''
            UPDATE clothes 
            SET {field} = ?
            WHERE id = ? AND user_id = ?
        ''', (value, item_id, user_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_clothing_categories(self, user_id):
        """Get all clothing categories for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT category FROM clothes 
            WHERE user_id = ?
        ''', (user_id,))
        
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return categories
    
    def save_outfit(self, user_id, name, description, clothes_ids, season=None, occasion=None):
        """Save a generated outfit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        clothes_ids_json = json.dumps(clothes_ids)
        
        cursor.execute('''
            INSERT INTO outfits (user_id, name, description, clothes_ids, season, occasion)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, description, clothes_ids_json, season, occasion))
        
        outfit_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return outfit_id
    
    def get_user_outfits(self, user_id):
        """Get all outfits for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM outfits 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        outfits = cursor.fetchall()
        conn.close()
        
        return outfits
    
    def update_user_preferences(self, user_id, style_preference=None, color_preference=None, season_preference=None):
        """Update user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences 
            (user_id, style_preference, color_preference, season_preference, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, style_preference, color_preference, season_preference, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_user_preferences(self, user_id):
        """Get user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_preferences 
            WHERE user_id = ?
        ''', (user_id,))
        
        preferences = cursor.fetchone()
        conn.close()
        
        return preferences 