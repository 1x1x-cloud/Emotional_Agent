"""
数据库操作模块
使用SQLite本地数据库
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 数据库文件路径
DB_PATH = "emotional_agent.db"


def init_database():
    """
    初始化数据库
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建会话表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # 创建消息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id TEXT,
        role TEXT,
        content TEXT,
        sentiment JSON,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id)
    )
    ''')
    
    # 创建情感日记表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emotion_diary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        date TEXT,
        emotion TEXT,
        intensity INTEGER,
        notes TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        UNIQUE(user_id, date)
    )
    ''')
    
    conn.commit()
    conn.close()


def get_db_connection():
    """
    获取数据库连接
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 允许通过列名访问
    return conn


def create_user(user_id: str, username: str = None, password_hash: str = None, email: str = None) -> bool:
    """
    创建用户（如果不存在）
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if username and password_hash:
            # 注册新用户
            cursor.execute(
                "INSERT OR IGNORE INTO users (id, username, password_hash, email, created_at, last_active) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, username, password_hash, email, datetime.now(), datetime.now())
            )
        else:
            # 兼容旧版本：创建匿名用户
            cursor.execute(
                "INSERT OR IGNORE INTO users (id, username, password_hash, created_at, last_active) VALUES (?, ?, ?, ?, ?)",
                (user_id, user_id, "", datetime.now(), datetime.now())
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"创建用户失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[Dict]:
    """
    根据用户名获取用户信息
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, username, password_hash, email, created_at, last_active FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "username": row["username"],
                "password_hash": row["password_hash"],
                "email": row["email"],
                "created_at": row["created_at"],
                "last_active": row["last_active"]
            }
        return None
    except Exception as e:
        print(f"获取用户失败: {e}")
        return None
    finally:
        conn.close()


def update_user_last_active(user_id: str) -> bool:
    """
    更新用户最后活跃时间
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE users SET last_active = ? WHERE id = ?",
            (datetime.now(), user_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"更新用户活跃时间失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def create_conversation(user_id: str, conversation_id: Optional[str] = None) -> str:
    """
    创建或获取会话
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 确保用户存在
        create_user(user_id)
        
        if conversation_id:
            # 检查会话是否存在
            cursor.execute(
                "SELECT id FROM conversations WHERE id = ?",
                (conversation_id,)
            )
            if cursor.fetchone():
                # 更新最后活跃时间
                cursor.execute(
                    "UPDATE conversations SET last_message_at = ? WHERE id = ?",
                    (datetime.now(), conversation_id)
                )
                conn.commit()
                return conversation_id
        
        # 创建新会话
        import uuid
        new_conversation_id = conversation_id or str(uuid.uuid4())
        
        cursor.execute(
            "INSERT INTO conversations (id, user_id, created_at, last_message_at) VALUES (?, ?, ?, ?)",
            (new_conversation_id, user_id, datetime.now(), datetime.now())
        )
        conn.commit()
        return new_conversation_id
    except Exception as e:
        print(f"创建会话失败: {e}")
        conn.rollback()
        # 回退到生成新ID
        import uuid
        return str(uuid.uuid4())
    finally:
        conn.close()


def save_message(conversation_id: str, role: str, content: str, sentiment: Optional[Dict] = None) -> bool:
    """
    保存消息
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content, sentiment, timestamp) VALUES (?, ?, ?, ?, ?)",
            (conversation_id, role, content, json.dumps(sentiment) if sentiment else None, datetime.now())
        )
        
        # 更新会话的最后消息时间
        cursor.execute(
            "UPDATE conversations SET last_message_at = ? WHERE id = ?",
            (datetime.now(), conversation_id)
        )
        
        conn.commit()
        return True
    except Exception as e:
        print(f"保存消息失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_user_conversations(user_id: str) -> List[Dict]:
    """
    获取用户的所有会话
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, created_at, last_message_at FROM conversations WHERE user_id = ? ORDER BY last_message_at DESC",
            (user_id,)
        )
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                "id": row["id"],
                "created_at": row["created_at"],
                "last_message_at": row["last_message_at"]
            })
        return conversations
    except Exception as e:
        print(f"获取会话失败: {e}")
        return []
    finally:
        conn.close()


def get_conversation_messages(conversation_id: str) -> List[Dict]:
    """
    获取会话的所有消息
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, role, content, sentiment, timestamp FROM messages WHERE conversation_id = ? ORDER BY timestamp",
            (conversation_id,)
        )
        messages = []
        for row in cursor.fetchall():
            sentiment = None
            if row["sentiment"]:
                try:
                    sentiment = json.loads(row["sentiment"])
                except:
                    sentiment = None
            
            messages.append({
                "id": row["id"],
                "role": row["role"],
                "content": row["content"],
                "sentiment": sentiment,
                "timestamp": row["timestamp"]
            })
        return messages
    except Exception as e:
        print(f"获取消息失败: {e}")
        return []


def get_user_sentiment_trend(user_id: str, days: int = 7) -> List[Dict]:
    """
    获取用户的情感趋势
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取用户的所有消息
        cursor.execute('''
            SELECT m.sentiment, m.timestamp 
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.user_id = ? 
            AND m.role = 'user' 
            AND m.timestamp >= datetime('now', '-' || ? || ' days')
            ORDER BY m.timestamp
        ''', (user_id, days))
        
        trend = []
        for row in cursor.fetchall():
            if row["sentiment"]:
                try:
                    sentiment = json.loads(row["sentiment"])
                    trend.append({
                        "timestamp": row["timestamp"],
                        "sentiment": sentiment.get("sentiment"),
                        "label": sentiment.get("label"),
                        "confidence": sentiment.get("confidence"),
                        "emotion": sentiment.get("emotion"),
                        "category": sentiment.get("category")
                    })
                except:
                    pass
        
        return trend
    except Exception as e:
        print(f"获取情感趋势失败: {e}")
        return []


def get_daily_sentiment_summary(user_id: str, days: int = 7) -> List[Dict]:
    """
    获取每日情感总结
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取用户的所有消息（按日期分组）
        cursor.execute('''
            SELECT 
                date(m.timestamp) as date,
                COUNT(*) as message_count,
                AVG(CASE WHEN m.sentiment LIKE '%"sentiment": true%' THEN 1 
                         WHEN m.sentiment LIKE '%"sentiment": false%' THEN -1 
                         ELSE 0 END) as avg_sentiment
            FROM messages m
            JOIN conversations c ON m.conversation_id = c.id
            WHERE c.user_id = ? 
            AND m.role = 'user' 
            AND m.timestamp >= datetime('now', '-' || ? || ' days')
            GROUP BY date(m.timestamp)
            ORDER BY date
        ''', (user_id, days))
        
        summary = []
        for row in cursor.fetchall():
            summary.append({
                "date": row["date"],
                "message_count": row["message_count"],
                "avg_sentiment": row["avg_sentiment"]
            })
        
        return summary
    except Exception as e:
        print(f"获取每日情感总结失败: {e}")
        return []


def save_emotion_diary(user_id: str, date: str, emotion: str, intensity: int, notes: str = None, tags: str = None) -> bool:
    """
    保存情感日记
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            '''INSERT OR REPLACE INTO emotion_diary (user_id, date, emotion, intensity, notes, tags, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (user_id, date, emotion, intensity, notes, tags, datetime.now())
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"保存情感日记失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def get_emotion_diary(user_id: str, date: str = None) -> Optional[Dict]:
    """
    获取情感日记
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if date:
            cursor.execute(
                "SELECT * FROM emotion_diary WHERE user_id = ? AND date = ?",
                (user_id, date)
            )
        else:
            cursor.execute(
                "SELECT * FROM emotion_diary WHERE user_id = ? ORDER BY date DESC LIMIT 1",
                (user_id,)
            )
        
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "date": row["date"],
                "emotion": row["emotion"],
                "intensity": row["intensity"],
                "notes": row["notes"],
                "tags": row["tags"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
        return None
    except Exception as e:
        print(f"获取情感日记失败: {e}")
        return None
    finally:
        conn.close()


def get_emotion_diary_list(user_id: str, days: int = 30) -> List[Dict]:
    """
    获取情感日记列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM emotion_diary WHERE user_id = ? AND date >= date('now', '-' || ? || ' days') ORDER BY date DESC",
            (user_id, days)
        )
        
        diaries = []
        for row in cursor.fetchall():
            diaries.append({
                "id": row["id"],
                "date": row["date"],
                "emotion": row["emotion"],
                "intensity": row["intensity"],
                "notes": row["notes"],
                "tags": row["tags"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })
        return diaries
    except Exception as e:
        print(f"获取情感日记列表失败: {e}")
        return []
    finally:
        conn.close()


# 初始化数据库
if __name__ == "__main__":
    init_database()
    print("数据库初始化完成")
    
    # 测试
    user_id = "test_user"
    conversation_id = create_conversation(user_id)
    print(f"创建会话: {conversation_id}")
    
    # 保存测试消息
    save_message(
        conversation_id,
        "user",
        "今天心情很好",
        {"sentiment": True, "label": "喜悦", "confidence": 0.95, "emotion": "joy", "category": "positive"}
    )
    
    save_message(
        conversation_id,
        "assistant",
        "很高兴听到你心情好！"
    )
    
    # 获取消息
    messages = get_conversation_messages(conversation_id)
    print(f"会话消息: {messages}")
    
    # 获取用户会话
    conversations = get_user_conversations(user_id)
    print(f"用户会话: {conversations}")
    
    # 获取情感趋势
    trend = get_user_sentiment_trend(user_id)
    print(f"情感趋势: {trend}")
