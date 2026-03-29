"""
智能推荐服务
基于用户情绪状态推荐适合的内容
"""

from typing import Dict, List, Optional
import random


class RecommendationService:
    """
    智能推荐服务
    """
    
    def __init__(self):
        # 音乐推荐库
        self.music_recommendations = {
            "joy": [
                {"title": "Happy", "artist": "Pharrell Williams", "reason": "欢快的节奏，适合愉悦的心情"},
                {"title": "阳光宅男", "artist": "周杰伦", "reason": "轻松愉快的旋律"},
                {"title": "Good Time", "artist": "Owl City", "reason": "充满活力的歌曲"},
                {"title": "小幸运", "artist": "田馥甄", "reason": "温暖甜美的歌曲"}
            ],
            "sadness": [
                {"title": "Someone Like You", "artist": "Adele", "reason": "悲伤但治愈的歌曲"},
                {"title": "后来", "artist": "刘若英", "reason": "温柔地陪伴你的情绪"},
                {"title": "Fix You", "artist": "Coldplay", "reason": "温暖治愈的旋律"},
                {"title": "夜空中最亮的星", "artist": "逃跑计划", "reason": "给你希望和力量"}
            ],
            "anxiety": [
                {"title": "Weightless", "artist": "Marconi Union", "reason": "科学证明最放松的音乐"},
                {"title": "River Flows in You", "artist": "Yiruma", "reason": "平静的钢琴曲"},
                {"title": "Clair de Lune", "artist": "Debussy", "reason": "古典音乐的宁静"},
                {"title": "天空之城", "artist": "久石让", "reason": "舒缓心灵的旋律"}
            ],
            "anger": [
                {"title": "Numb", "artist": "Linkin Park", "reason": "释放情绪的摇滚"},
                {"title": "倔强", "artist": "五月天", "reason": "将愤怒转化为力量"},
                {"title": "Stronger", "artist": "Kelly Clarkson", "reason": "让你更坚强"},
                {"title": "Fight Song", "artist": "Rachel Platten", "reason": "激励人心的歌曲"}
            ],
            "loneliness": [
                {"title": "Someone You Loved", "artist": "Lewis Capaldi", "reason": "陪伴你的孤独"},
                {"title": "消愁", "artist": "毛不易", "reason": "理解你的感受"},
                {"title": "Let Her Go", "artist": "Passenger", "reason": "温柔的陪伴"},
                {"title": "像我这样的人", "artist": "毛不易", "reason": "共鸣与理解"}
            ],
            "fatigue": [
                {"title": "Perfect", "artist": "Ed Sheeran", "reason": "温柔放松的歌曲"},
                {"title": "慢慢喜欢你", "artist": "莫文蔚", "reason": "舒缓的节奏"},
                {"title": "Can You Feel the Love Tonight", "artist": "Elton John", "reason": "温暖的旋律"},
                {"title": "月亮代表我的心", "artist": "邓丽君", "reason": "经典放松歌曲"}
            ],
            "neutral": [
                {"title": "Shape of You", "artist": "Ed Sheeran", "reason": "轻快的流行歌曲"},
                {"title": "告白气球", "artist": "周杰伦", "reason": "甜蜜轻松的歌曲"},
                {"title": "Counting Stars", "artist": "OneRepublic", "reason": "积极向上的歌曲"},
                {"title": "演员", "artist": "薛之谦", "reason": "深情动人的歌曲"}
            ]
        }
        
        # 文章/内容推荐库
        self.article_recommendations = {
            "joy": [
                {"title": "如何保持积极心态", "category": "心理成长", "reason": "分享快乐的方法"},
                {"title": "感恩日记的力量", "category": "自我提升", "reason": "记录美好时刻"},
                {"title": "成功人士的早晨习惯", "category": "生活方式", "reason": "保持好状态"}
            ],
            "sadness": [
                {"title": "如何面对失落感", "category": "情绪管理", "reason": "理解和接纳悲伤"},
                {"title": "哭泣是治愈的良药", "category": "心理健康", "reason": "释放情绪的重要性"},
                {"title": "从挫折中成长", "category": "个人成长", "reason": "困难是成长的机会"}
            ],
            "anxiety": [
                {"title": "5分钟冥想指南", "category": "放松技巧", "reason": "快速缓解焦虑"},
                {"title": "深呼吸的艺术", "category": "身心健康", "reason": "简单有效的放松方法"},
                {"title": "如何应对压力", "category": "压力管理", "reason": "实用的减压技巧"}
            ],
            "anger": [
                {"title": "愤怒管理的智慧", "category": "情绪控制", "reason": "健康地表达愤怒"},
                {"title": "运动释放负面情绪", "category": "健康生活", "reason": "用运动转化情绪"},
                {"title": "正念与情绪调节", "category": "心理健康", "reason": "平静内心的方法"}
            ],
            "loneliness": [
                {"title": "独处的美好", "category": "自我成长", "reason": "享受独处时光"},
                {"title": "建立深层连接的方法", "category": "人际关系", "reason": "改善社交质量"},
                {"title": "自我陪伴的力量", "category": "心理健康", "reason": "成为自己的朋友"}
            ],
            "fatigue": [
                {"title": "优质睡眠指南", "category": "健康生活", "reason": "改善睡眠质量"},
                {"title": "工作与生活平衡", "category": "生活方式", "reason": "避免过度疲劳"},
                {"title": "恢复精力的方法", "category": "身心健康", "reason": "快速恢复活力"}
            ],
            "neutral": [
                {"title": "培养新兴趣的好处", "category": "个人发展", "reason": "丰富生活内容"},
                {"title": "每日小确幸", "category": "生活态度", "reason": "发现生活美好"},
                {"title": "持续学习的重要性", "category": "自我提升", "reason": "保持好奇心"}
            ]
        }
        
        # 活动推荐库
        self.activity_recommendations = {
            "joy": [
                {"activity": "与朋友分享快乐", "reason": "快乐会传染"},
                {"activity": "记录美好时刻", "reason": "留住快乐回忆"},
                {"activity": "尝试新事物", "reason": "保持好奇心"}
            ],
            "sadness": [
                {"activity": "散步或轻度运动", "reason": "运动产生多巴胺"},
                {"activity": "写日记", "reason": "倾诉和整理情绪"},
                {"activity": "看一部治愈电影", "reason": "转移注意力"}
            ],
            "anxiety": [
                {"activity": "深呼吸练习", "reason": "快速放松身心"},
                {"activity": "瑜伽或冥想", "reason": "平静内心"},
                {"activity": "整理房间", "reason": "环境整洁有助于心情"}
            ],
            "anger": [
                {"activity": "剧烈运动", "reason": "释放负面情绪"},
                {"activity": "冷水洗脸", "reason": "物理降温"},
                {"activity": "暂时离开现场", "reason": "避免冲动行为"}
            ],
            "loneliness": [
                {"activity": "联系老朋友", "reason": "重建社交连接"},
                {"activity": "参加兴趣小组", "reason": "认识新朋友"},
                {"activity": "养宠物或植物", "reason": "获得陪伴感"}
            ],
            "fatigue": [
                {"activity": "小憩片刻", "reason": "恢复精力"},
                {"activity": "泡个热水澡", "reason": "放松身心"},
                {"activity": "听轻音乐", "reason": "舒缓疲劳"}
            ],
            "neutral": [
                {"activity": "阅读一本书", "reason": "丰富内心世界"},
                {"activity": "学习新技能", "reason": "提升自我"},
                {"activity": "户外散步", "reason": "呼吸新鲜空气"}
            ]
        }
    
    def get_music_recommendation(self, emotion: str, count: int = 3) -> List[Dict]:
        """
        获取音乐推荐
        """
        recommendations = self.music_recommendations.get(emotion, self.music_recommendations["neutral"])
        return random.sample(recommendations, min(count, len(recommendations)))
    
    def get_article_recommendation(self, emotion: str, count: int = 2) -> List[Dict]:
        """
        获取文章推荐
        """
        recommendations = self.article_recommendations.get(emotion, self.article_recommendations["neutral"])
        return random.sample(recommendations, min(count, len(recommendations)))
    
    def get_activity_recommendation(self, emotion: str, count: int = 2) -> List[Dict]:
        """
        获取活动推荐
        """
        recommendations = self.activity_recommendations.get(emotion, self.activity_recommendations["neutral"])
        return random.sample(recommendations, min(count, len(recommendations)))
    
    def get_full_recommendation(self, emotion: str) -> Dict:
        """
        获取完整的推荐内容
        """
        return {
            "emotion": emotion,
            "music": self.get_music_recommendation(emotion),
            "articles": self.get_article_recommendation(emotion),
            "activities": self.get_activity_recommendation(emotion),
            "message": self._get_recommendation_message(emotion)
        }
    
    def _get_recommendation_message(self, emotion: str) -> str:
        """
        获取推荐消息
        """
        messages = {
            "joy": "很高兴看到您心情愉快！这里有一些内容可以让您保持这份好心情。",
            "sadness": "我理解您现在可能感到难过。这里有一些内容希望能给您带来些许安慰。",
            "anxiety": "感到焦虑是正常的。这里有一些放松的方法，希望能帮助您平静下来。",
            "anger": "愤怒是一种正常的情绪。这里有一些方法可以帮助您健康地表达和转化它。",
            "loneliness": "孤独感是很多人都会经历的。这里有一些建议，希望能给您带来温暖。",
            "fatigue": "您看起来需要休息。这里有一些恢复精力的建议。",
            "neutral": "这里有一些有趣的内容，希望能为您的生活增添一些色彩。"
        }
        return messages.get(emotion, messages["neutral"])


# 全局推荐服务实例
recommendation_service = RecommendationService()


def get_recommendations(emotion: str) -> Dict:
    """获取推荐接口"""
    return recommendation_service.get_full_recommendation(emotion)


# 测试
if __name__ == "__main__":
    # 测试推荐功能
    recommendations = get_recommendations("sadness")
    print("推荐内容:")
    print(f"情绪: {recommendations['emotion']}")
    print(f"消息: {recommendations['message']}")
    print("\n音乐推荐:")
    for music in recommendations['music']:
        print(f"  - {music['title']} by {music['artist']} ({music['reason']})")
    print("\n文章推荐:")
    for article in recommendations['articles']:
        print(f"  - {article['title']} ({article['category']}) - {article['reason']}")
    print("\n活动推荐:")
    for activity in recommendations['activities']:
        print(f"  - {activity['activity']} ({activity['reason']})")
