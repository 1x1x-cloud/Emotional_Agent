"""
实时情感监测与干预模块
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


class EmotionMonitor:
    """
    情感监测器
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.emotion_history = []  # 存储最近的情感记录
        self.max_history = 50  # 最大历史记录数
        self.warning_threshold = 3  # 连续负面情绪警告阈值
        self.intervention_threshold = 5  # 连续负面情绪干预阈值
    
    def add_emotion_record(self, emotion: str, sentiment: bool, confidence: float):
        """
        添加情感记录
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion,
            "sentiment": sentiment,
            "confidence": confidence
        }
        
        self.emotion_history.append(record)
        
        # 保持历史记录在最大限制内
        if len(self.emotion_history) > self.max_history:
            self.emotion_history = self.emotion_history[-self.max_history:]
        
        return record
    
    def get_recent_emotions(self, minutes: int = 30) -> List[Dict]:
        """
        获取最近一段时间的情感记录
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent = []
        
        for record in reversed(self.emotion_history):
            record_time = datetime.fromisoformat(record["timestamp"])
            if record_time >= cutoff_time:
                recent.append(record)
            else:
                break
        
        return list(reversed(recent))
    
    def analyze_emotion_trend(self) -> Dict:
        """
        分析情感趋势
        """
        if not self.emotion_history:
            return {
                "trend": "stable",
                "current_emotion": "neutral",
                "emotion_changes": 0,
                "negative_streak": 0
            }
        
        # 最近的情感
        recent = self.emotion_history[-5:] if len(self.emotion_history) >= 5 else self.emotion_history
        
        # 计算负面情绪连续次数
        negative_streak = 0
        for record in reversed(recent):
            if record["sentiment"] is False:
                negative_streak += 1
            else:
                break
        
        # 分析情绪变化
        emotion_changes = 0
        if len(recent) >= 2:
            for i in range(1, len(recent)):
                if recent[i]["emotion"] != recent[i-1]["emotion"]:
                    emotion_changes += 1
        
        # 判断趋势
        positive_count = sum(1 for r in recent if r["sentiment"] is True)
        negative_count = sum(1 for r in recent if r["sentiment"] is False)
        
        if positive_count > negative_count:
            trend = "improving"
        elif negative_count > positive_count:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "current_emotion": recent[-1]["emotion"] if recent else "neutral",
            "emotion_changes": emotion_changes,
            "negative_streak": negative_streak
        }
    
    def check_emotion_alert(self) -> Optional[Dict]:
        """
        检查情绪预警
        """
        trend = self.analyze_emotion_trend()
        
        # 连续负面情绪干预（先检查更严重的情况）
        if trend["negative_streak"] >= self.intervention_threshold:
            return {
                "level": "intervention",
                "message": f"重要提醒：您已经连续{trend['negative_streak']}次表达负面情绪",
                "recommendation": "建议您与朋友或家人交流，或考虑寻求专业帮助",
                "negative_streak": trend["negative_streak"]
            }
        
        # 连续负面情绪警告
        if trend["negative_streak"] >= self.warning_threshold:
            return {
                "level": "warning",
                "message": f"注意：您已经连续{trend['negative_streak']}次表达负面情绪",
                "recommendation": "建议您休息一下，或尝试做些让自己开心的事情",
                "negative_streak": trend["negative_streak"]
            }
        
        return None
    
    def get_intervention_suggestion(self) -> Optional[str]:
        """
        获取干预建议
        """
        alert = self.check_emotion_alert()
        if alert:
            return alert["recommendation"]
        
        # 基于当前情绪的建议
        trend = self.analyze_emotion_trend()
        current_emotion = trend["current_emotion"]
        
        emotion_suggestions = {
            "sadness": "如果您感到难过，可以尝试听一些舒缓的音乐，或与朋友聊聊天",
            "anxiety": "如果您感到焦虑，可以尝试深呼吸或冥想，让自己平静下来",
            "anger": "如果您感到愤怒，可以尝试暂时离开让您生气的环境，或进行一些体育活动",
            "loneliness": "如果您感到孤独，可以尝试主动联系朋友，或参加一些社交活动",
            "fatigue": "如果您感到疲惫，建议您好好休息，保证充足的睡眠",
            "joy": "很高兴看到您心情不错！继续保持这份好心情吧",
            "gratitude": "感恩的心情对心理健康非常有益，继续保持这种积极的态度",
            "contentment": "满足的状态是一种很好的心理状态，享受当下的美好时光"
        }
        
        return emotion_suggestions.get(current_emotion)
    
    def reset(self):
        """
        重置情感监测
        """
        self.emotion_history = []


# 全局情感监测器实例
emotion_monitors = {}


def get_emotion_monitor(user_id: str) -> EmotionMonitor:
    """
    获取或创建情感监测器
    """
    if user_id not in emotion_monitors:
        emotion_monitors[user_id] = EmotionMonitor(user_id)
    return emotion_monitors[user_id]


def add_emotion_record(user_id: str, emotion: str, sentiment: bool, confidence: float):
    """
    添加情感记录
    """
    monitor = get_emotion_monitor(user_id)
    return monitor.add_emotion_record(emotion, sentiment, confidence)


def check_emotion_alert(user_id: str) -> Optional[Dict]:
    """
    检查情绪预警
    """
    monitor = get_emotion_monitor(user_id)
    return monitor.check_emotion_alert()


def get_intervention_suggestion(user_id: str) -> Optional[str]:
    """
    获取干预建议
    """
    monitor = get_emotion_monitor(user_id)
    return monitor.get_intervention_suggestion()


def get_emotion_trend(user_id: str) -> Dict:
    """
    获取情感趋势
    """
    monitor = get_emotion_monitor(user_id)
    return monitor.analyze_emotion_trend()


def reset_emotion_monitor(user_id: str):
    """
    重置情感监测器
    """
    if user_id in emotion_monitors:
        emotion_monitors[user_id].reset()


# 测试
if __name__ == "__main__":
    # 创建监测器
    monitor = EmotionMonitor("test_user")
    
    # 添加一些情感记录
    test_emotions = [
        ("sadness", False, 0.8),
        ("sadness", False, 0.7),
        ("sadness", False, 0.9),
        ("anxiety", False, 0.8),
        ("anxiety", False, 0.7)
    ]
    
    for emotion, sentiment, confidence in test_emotions:
        monitor.add_emotion_record(emotion, sentiment, confidence)
    
    # 分析趋势
    trend = monitor.analyze_emotion_trend()
    print("情感趋势:", json.dumps(trend, ensure_ascii=False, indent=2))
    
    # 检查预警
    alert = monitor.check_emotion_alert()
    print("情绪预警:", json.dumps(alert, ensure_ascii=False, indent=2))
    
    # 获取干预建议
    suggestion = monitor.get_intervention_suggestion()
    print("干预建议:", suggestion)
