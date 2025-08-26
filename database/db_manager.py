import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Khởi tạo database và các bảng"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Bảng messages (queue)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                sender TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                naive_bayes_score REAL,
                llm_score REAL,
                classification TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            )
        ''')
        
        # Bảng logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS filter_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                step TEXT,
                result TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES messages (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_message(self, content: str, sender: str) -> int:
        """Thêm message vào queue"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO messages (content, sender) VALUES (?, ?)",
            (content, sender)
        )
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_pending_messages(self) -> List[Dict]:
        """Lấy các message chưa xử lý"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM messages WHERE status = 'pending' ORDER BY created_at"
        )
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return messages
    
    def update_message_status(self, message_id: int, status: str, 
                            classification: str = None, 
                            naive_bayes_score: float = None,
                            llm_score: float = None):
        """Cập nhật trạng thái message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        update_fields = ["status = ?", "processed_at = CURRENT_TIMESTAMP"]
        values = [status]
        
        if classification:
            update_fields.append("classification = ?")
            values.append(classification)
        
        if naive_bayes_score is not None:
            update_fields.append("naive_bayes_score = ?")
            values.append(naive_bayes_score)
            
        if llm_score is not None:
            update_fields.append("llm_score = ?")
            values.append(llm_score)
        
        values.append(message_id)
        
        query = f"UPDATE messages SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
    
    def log_filter_step(self, message_id: int, step: str, result: str, details: str = None):
        """Ghi log các bước filter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO filter_logs (message_id, step, result, details) VALUES (?, ?, ?, ?)",
            (message_id, step, result, details or "")
        )
        
        conn.commit()
        conn.close()
    
    def get_inbox_messages(self, status: str = 'approved') -> List[Dict]:
        """Lấy messages trong inbox"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM messages WHERE status = ? ORDER BY created_at DESC",
            (status,)
        )
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return messages
    
    def get_all_messages_with_logs(self) -> List[Dict]:
        """Lấy tất cả messages kèm logs để debug"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = '''
            SELECT m.*, 
                   GROUP_CONCAT(
                       fl.step || ': ' || fl.result || 
                       CASE WHEN fl.details != '' THEN ' (' || fl.details || ')' ELSE '' END
                       , ' | '
                   ) as filter_history
            FROM messages m
            LEFT JOIN filter_logs fl ON m.id = fl.message_id
            GROUP BY m.id
            ORDER BY m.created_at DESC
        '''
        
        cursor.execute(query)
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return messages