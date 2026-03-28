"""
用户画像与情感趋势分析模块
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


def analyze_user_profile(user_messages: List[Dict]) -> Dict:
    """
    分析用户画像
    """
    if not user_messages:
        return {
            "total_messages": 0,
            "emotion_distribution": {},
            "common_topics": [],
            "emotion_patterns": [],
            "peak_hours": []
        }
    
    # 1. 情绪分布
    emotion_distribution = {}
    for msg in user_messages:
        sentiment = msg.get("sentiment", {})
        emotion = sentiment.get("emotion", "neutral")
        if emotion:
            emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1
    
    # 2. 常用话题（基于关键词）
    common_topics = extract_common_topics(user_messages)
    
    # 3. 情绪模式
    emotion_patterns = analyze_emotion_patterns(user_messages)
    
    # 4. 活跃时段
    peak_hours = analyze_peak_hours(user_messages)
    
    return {
        "total_messages": len(user_messages),
        "emotion_distribution": emotion_distribution,
        "common_topics": common_topics,
        "emotion_patterns": emotion_patterns,
        "peak_hours": peak_hours
    }


def extract_common_topics(messages: List[Dict]) -> List[str]:
    """
    提取常用话题
    """
    topic_keywords = {
        "工作": ["工作", "同事", "老板", "项目", "任务", "加班", "压力"],
        "学习": ["学习", "考试", "作业", "成绩", "课程", "老师"],
        "感情": ["恋爱", "分手", "喜欢", "爱", "关系", "朋友"],
        "家庭": ["家人", "父母", "孩子", "家", "生活", "照顾"],
        "健康": ["身体", "生病", "医院", "锻炼", "睡眠", "累"],
        "娱乐": ["游戏", "电影", "音乐", "旅行", "玩", "开心"]
    }
    
    topic_counts = {topic: 0 for topic in topic_keywords}
    
    for msg in messages:
        content = msg.get("content", "").lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in content for keyword in keywords):
                topic_counts[topic] += 1
    
    # 返回出现次数最多的前3个话题
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    return [topic for topic, count in sorted_topics[:3] if count > 0]


def analyze_emotion_patterns(messages: List[Dict]) -> List[Dict]:
    """
    分析情绪模式
    """
    if len(messages) < 3:
        return []
    
    patterns = []
    
    # 计算连续情绪变化
    for i in range(1, len(messages)):
        prev_msg = messages[i - 1]
        curr_msg = messages[i]
        
        prev_sentiment = prev_msg.get("sentiment", {})
        curr_sentiment = curr_msg.get("sentiment", {})
        
        prev_category = prev_sentiment.get("category", "neutral")
        curr_category = curr_sentiment.get("category", "neutral")
        
        if prev_category != curr_category:
            patterns.append({
                "from": prev_category,
                "to": curr_category,
                "timestamp": curr_msg.get("timestamp")
            })
    
    return patterns


def analyze_peak_hours(messages: List[Dict]) -> List[Dict]:
    """
    分析活跃时段
    """
    hour_counts = {}
    
    for msg in messages:
        timestamp = msg.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
                hour = dt.hour
                hour_counts[hour] = hour_counts.get(hour, 0) + 1
            except:
                pass
    
    # 返回活跃时段（按小时排序）
    sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"hour": hour, "count": count} for hour, count in sorted_hours[:5]]


def analyze_emotion_trend(messages: List[Dict], days: int = 7) -> Dict:
    """
    分析情感趋势
    """
    if not messages:
        return {
            "trend": "stable",
            "positive_ratio": 0,
            "negative_ratio": 0,
            "dominant_emotion": "neutral",
            "emotion_changes": 0,
            "recommendations": []
        }
    
    # 1. 计算正负向比例
    positive_count = sum(1 for msg in messages 
                     if msg.get("sentiment", {}).get("sentiment") == True)
    negative_count = sum(1 for msg in messages 
                     if msg.get("sentiment", {}).get("sentiment") == False)
    total = len(messages)
    
    positive_ratio = positive_count / total if total > 0 else 0
    negative_ratio = negative_count / total if total > 0 else 0
    
    # 2. 判断主导情绪
    emotion_counts = {}
    for msg in messages:
        emotion = msg.get("sentiment", {}).get("emotion", "neutral")
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "neutral"
    
    # 3. 分析趋势方向
    if len(messages) >= 3:
        recent = messages[-3:]
        positive_recent = sum(1 for msg in recent 
                         if msg.get("sentiment", {}).get("sentiment") == True)
        
        if positive_recent >= 2:
            trend = "improving"
        elif positive_recent == 0:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"
    
    # 4. 计算情绪变化频率
    emotion_changes = len(analyze_emotion_patterns(messages))
    
    # 5. 生成建议
    recommendations = generate_recommendations(positive_ratio, negative_ratio, dominant_emotion, trend)
    
    return {
        "trend": trend,
        "positive_ratio": round(positive_ratio, 2),
        "negative_ratio": round(negative_ratio, 2),
        "dominant_emotion": dominant_emotion,
        "emotion_changes": emotion_changes,
        "recommendations": recommendations
    }


def generate_recommendations(positive_ratio: float, negative_ratio: float, 
                       dominant_emotion: str, trend: str) -> List[str]:
    """
    生成个性化建议
    """
    recommendations = []
    
    # 基于正向比例的建议
    if positive_ratio > 0.7:
        recommendations.append("你的整体情绪很积极，继续保持这种好心情！")
    elif negative_ratio > 0.6:
        recommendations.append("最近负面情绪较多，建议多和朋友聊天或进行户外活动。")
    
    # 基于主导情绪的建议
    emotion_recommendations = {
        "joy": "你经常感到开心，这很好！可以尝试分享你的快乐给更多人。",
        "anxiety": "你最近比较焦虑，建议尝试冥想或深呼吸来放松心情。",
        "sadness": "你最近有些低落，记得给自己一些关爱，不要独自承受。",
        "anger": "你最近容易生气，建议运动或听音乐来缓解压力。",
        "loneliness": "你感到孤独，建议主动联系朋友或参加社交活动。",
        "fatigue": "你比较疲惫，建议保证充足的睡眠和休息。",
        "neutral": "你的情绪比较平稳，可以尝试寻找一些新的兴趣爱好。"
    }
    
    if dominant_emotion in emotion_recommendations:
        recommendations.append(emotion_recommendations[dominant_emotion])
    
    # 基于趋势的建议
    if trend == "declining":
        recommendations.append("情绪有下降趋势，建议关注自己的心理状态，必要时寻求专业帮助。")
    elif trend == "improving":
        recommendations.append("情绪正在好转，继续保持！")
    
    return recommendations


def get_emotion_summary(messages: List[Dict]) -> Dict:
    """
    获取情感总结
    """
    if not messages:
        return {
            "total": 0,
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }
    
    positive = sum(1 for msg in messages 
                 if msg.get("sentiment", {}).get("sentiment") == True)
    negative = sum(1 for msg in messages 
                 if msg.get("sentiment", {}).get("sentiment") == False)
    neutral = sum(1 for msg in messages 
                if msg.get("sentiment", {}).get("sentiment") is None)
    
    return {
        "total": len(messages),
        "positive": positive,
        "negative": negative,
        "neutral": neutral
    }


# 测试
if __name__ == "__main__":
    test_messages = [
        {
            "content": "今天心情很好",
            "sentiment": {"sentiment": True, "emotion": "joy", "category": "positive"},
            "timestamp": "2026-03-28 10:00:00"
        },
        {
            "content": "工作压力好大",
            "sentiment": {"sentiment": False, "emotion": "anxiety", "category": "negative"},
            "timestamp": "2026-03-28 14:00:00"
        },
        {
            "content": "感觉好孤独",
            "sentiment": {"sentiment": False, "emotion": "loneliness", "category": "negative"},
            "timestamp": "2026-03-28 18:00:00"
        }
    ]
    
    profile = analyze_user_profile(test_messages)
    print("用户画像:", json.dumps(profile, ensure_ascii=False, indent=2))
    
    trend = analyze_emotion_trend(test_messages)
    print("情感趋势:", json.dumps(trend, ensure_ascii=False, indent=2))
