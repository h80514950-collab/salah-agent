"""
SQLite Database Manager for Salah Agent
Handles user profiles, voice embeddings, and command logs
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path="data/salah_agent.db"):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist"""
        # Users table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                voice_embedding TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP,
                is_authorized INTEGER DEFAULT 1
            )
        """)
        
        # Commands log table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                command TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success INTEGER DEFAULT 1,
                response TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        
        # System log table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def register_user(self, name, voice_embedding):
        """
        Register a new user with voice embedding
        
        Args:
            name: User name
            voice_embedding: Numpy array as list (JSON serializable)
        
        Returns:
            user_id if successful, None otherwise
        """
        try:
            embedding_json = json.dumps(voice_embedding.tolist() if hasattr(voice_embedding, 'tolist') else voice_embedding)
            self.cursor.execute(
                "INSERT INTO users (name, voice_embedding) VALUES (?, ?)",
                (name, embedding_json)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"❌ User '{name}' already exists")
            return None
        except Exception as e:
            print(f"❌ Error registering user: {e}")
            return None
    
    def get_user_by_name(self, name):
        """Get user record by name"""
        self.cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'voice_embedding': json.loads(result[2]),
                'created_at': result[3],
                'last_seen': result[4],
                'is_authorized': result[5]
            }
        return None
    
    def get_all_users(self):
        """Get all registered users"""
        self.cursor.execute("SELECT id, name, voice_embedding, is_authorized FROM users WHERE is_authorized = 1")
        users = []
        for row in self.cursor.fetchall():
            users.append({
                'id': row[0],
                'name': row[1],
                'voice_embedding': json.loads(row[2]),
                'is_authorized': row[3]
            })
        return users
    
    def update_last_seen(self, user_id):
        """Update user's last_seen timestamp"""
        try:
            self.cursor.execute(
                "UPDATE users SET last_seen = ? WHERE id = ?",
                (datetime.now().isoformat(), user_id)
            )
            self.conn.commit()
        except Exception as e:
            print(f"❌ Error updating last_seen: {e}")
    
    def log_command(self, user_id, command, success=True, response=None):
        """Log a command execution"""
        try:
            self.cursor.execute(
                "INSERT INTO command_log (user_id, command, success, response) VALUES (?, ?, ?, ?)",
                (user_id, command, 1 if success else 0, response)
            )
            self.conn.commit()
        except Exception as e:
            print(f"❌ Error logging command: {e}")
    
    def log_system(self, level, message):
        """Log system event"""
        try:
            self.cursor.execute(
                "INSERT INTO system_log (level, message) VALUES (?, ?)",
                (level, message)
            )
            self.conn.commit()
        except Exception as e:
            print(f"❌ Error logging system event: {e}")
    
    def get_command_history(self, user_id, limit=10):
        """Get recent commands for a user"""
        self.cursor.execute(
            "SELECT command, timestamp, success FROM command_log WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
        )
        return self.cursor.fetchall()
    
    def delete_user(self, name):
        """Remove a user from the system"""
        try:
            self.cursor.execute("DELETE FROM users WHERE name = ?", (name,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Error deleting user: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
