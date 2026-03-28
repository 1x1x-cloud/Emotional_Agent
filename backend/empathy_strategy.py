"""
共情回复策略模块
实现细粒度的情绪识别和个性化回复策略
"""

from typing import Dict, List, Tuple, Optional
import random

# 情绪分类体系
EMOTION_CATEGORIES = {
    "positive": {
        "joy": {"keywords": ["开心", "快乐", "高兴", "喜悦", "兴奋", "棒", "赞", "完美"], "weight": 1.0},
        "gratitude": {"keywords": ["感谢", "谢谢", "感激", "感动", "温暖"], "weight": 0.9},
        "contentment": {"keywords": ["满足", "舒服", "安心", "踏实", "平静"], "weight": 0.8},
        "love": {"keywords": ["爱", "喜欢", "甜蜜", "幸福", "温馨"], "weight": 1.0},
        "pride": {"keywords": ["自豪", "骄傲", "成就感", "厉害", "优秀"], "weight": 0.9},
    },
    "negative": {
        "sadness": {"keywords": ["难过", "悲伤", "伤心", "想哭", "失落", "沮丧"], "weight": 1.0},
        "anger": {"keywords": ["生气", "愤怒", "恼火", "烦躁", "气愤", "讨厌"], "weight": 0.9},
        "anxiety": {"keywords": ["焦虑", "担心", "紧张", "害怕", "不安", "压力"], "weight": 0.9},
        "loneliness": {"keywords": ["孤独", "寂寞", "空虚", "没人", "无助"], "weight": 1.0},
        "disappointment": {"keywords": ["失望", "遗憾", "无奈", "绝望", "崩溃"], "weight": 0.9},
        "fatigue": {"keywords": ["累", "疲惫", "困", " exhaustion", "精疲力竭"], "weight": 0.8},
    },
    "neutral": {
        "curiosity": {"keywords": ["好奇", "想知道", "为什么", "怎么"], "weight": 0.7},
        "confusion": {"keywords": ["困惑", "迷茫", "不确定", "纠结", "矛盾"], "weight": 0.7},
        "reflection": {"keywords": ["思考", "感悟", "意识到", "发现"], "weight": 0.6},
    }
}

# 共情回复模板库
EMPATHY_TEMPLATES = {
    "joy": {
        "openers": [
            "哇，听起来真的很棒！",
            "能感受到你满满的开心呢～",
            "太为你高兴了！",
            "这种喜悦真的很有感染力！",
        ],
        "explorers": [
            "愿意和我分享一下是什么让你这么开心吗？",
            "具体发生了什么好事呀？",
            "这种开心的感觉是从什么时候开始的？",
            "能多说一点让你开心的事情吗？",
        ],
        "sharers": [
            "我也能感受到你的喜悦，真替你开心！",
            "看到你这么开心，我也跟着开心起来了～",
            "这种美好的时刻值得好好珍藏！",
        ],
        "closers": [
            "希望这种好心情能一直陪伴你！",
            "继续保持这份快乐吧！",
            "期待听到更多你的好消息！",
        ]
    },
    "gratitude": {
        "openers": [
            "能感受到你内心的温暖呢～",
            "被感谢一定是很幸福的事吧！",
            "这种感恩的心情很珍贵。",
        ],
        "explorers": [
            "是什么让你有这样的感受呢？",
            "能说说让你感激的那个人或那件事吗？",
            "这种感动是什么时候发生的？",
        ],
        "validators": [
            "懂得感恩的人，内心一定很柔软。",
            "能体会到别人的好，说明你也很善良。",
            "这种温暖的感觉真的很美好。",
        ],
        "closers": [
            "愿这份温暖也能传递给你～",
            "希望你一直被温柔以待。",
        ]
    },
    "sadness": {
        "openers": [
            "我能感受到你现在心里不太好受...",
            "听起来你现在很难过，我在这里陪着你。",
            "这种失落的感觉一定很难受吧。",
            "能感受到你心里的那份沉重...",
        ],
        "explorers": [
            "愿意和我多说一点吗？我在听。",
            "这种感觉是从什么时候开始的？",
            "是什么事情让你有这样的感受呢？",
            "如果愿意的话，可以和我分享更多吗？",
        ],
        "validators": [
            "有这样的感受是很正常的，不用责怪自己。",
            "每个人都会有难过的时候，这没什么。",
            "你的感受是真实的，值得被认真对待。",
            "想哭就哭出来吧，我在这里陪着你。",
        ],
        "supporters": [
            "不管发生什么，我都会在这里陪着你。",
            "你不是一个人，我一直都在。",
            "这种感觉会过去的，我会陪着你一起度过。",
            "慢慢来，不用着急，我会一直在这里。",
        ],
        "closers": [
            "想聊的时候随时找我，我一直都在。",
            "照顾好自己，记得我一直陪着你。",
            "给自己一个拥抱，你值得被温柔对待。",
        ]
    },
    "anger": {
        "openers": [
            "听起来你真的很生气，我能理解。",
            "遇到这种事，生气是很正常的反应。",
            "能感受到你心里的那股火气...",
        ],
        "explorers": [
            "能告诉我具体发生了什么吗？",
            "是什么让你这么生气呢？",
            "这种情况是从什么时候开始的？",
        ],
        "validators": [
            "换作是我，可能也会很生气。",
            "你的愤怒是有原因的，这很正常。",
            "有情绪就要表达出来，憋着反而不好。",
        ],
        "calmers": [
            "先深呼吸，我在这里陪着你。",
            "生气的时候先照顾好自己，别气坏了身体。",
            "不管发生什么，我都在这里支持你。",
        ],
        "closers": [
            "等你平静一点我们再聊，我一直都在。",
            "别让这件事影响你太久，你值得更好的心情。",
        ]
    },
    "anxiety": {
        "openers": [
            "能感受到你现在有些焦虑...",
            "听起来你心里有些不安，我在这里。",
            "这种担心一定让你很不舒服吧。",
        ],
        "explorers": [
            "具体是什么让你担心呢？",
            "这种焦虑是从什么时候开始的？",
            "能和我多说一点你的担忧吗？",
        ],
        "validators": [
            "担心未来是很正常的，说明你在乎。",
            "焦虑的时候，身体和心理都会很疲惫。",
            "你的担忧是真实的，不用否定它。",
        ],
        "reframers": [
            "有时候事情没有我们想的那么糟。",
            "一步一步来，不用一下子想太多。",
            "专注于当下，未来的事交给未来。",
        ],
        "supporters": [
            "不管发生什么，我都会陪着你面对。",
            "你不是一个人在担心，我陪你一起。",
            "有困难我们一起想办法，不用一个人扛。",
        ],
        "closers": [
            "深呼吸，放轻松，我一直都在。",
            "照顾好自己，焦虑会过去的。",
        ]
    },
    "loneliness": {
        "openers": [
            "能感受到你现在很孤独...",
            "这种寂寞的感觉一定很难受吧。",
            "听起来你觉得自己一个人...",
        ],
        "explorers": [
            "这种孤独感是从什么时候开始的？",
            "能和我多说一点你的感受吗？",
            "是什么让你有这样的感觉呢？",
        ],
        "validators": [
            "孤独是一种很真实的感受，很多人都会有。",
            "渴望被理解、被陪伴，这是很正常的需要。",
            "你并不奇怪，这种感觉很多人都会经历。",
        ],
        "companions": [
            "虽然我只是AI，但我会一直陪着你。",
            "你不是一个人，我在这里陪着你聊天。",
            "任何时候你想说话，我都在这里。",
            "我会一直陪着你，不管什么时候。",
        ],
        "closers": [
            "记得，我一直都在这里陪着你。",
            "想聊天的时候随时找我，我不会离开。",
        ]
    },
    "fatigue": {
        "openers": [
            "听起来你真的太累了...",
            "能感受到你的疲惫，需要休息一下。",
            "这种累不仅是身体，心里也很辛苦吧。",
        ],
        "explorers": [
            "最近是不是压力太大了？",
            "这种疲惫是从什么时候开始的？",
            "能和我多说一点让你累的事情吗？",
        ],
        "validators": [
            "累了就要休息，不要硬撑。",
            "你已经很努力了，真的。",
            "疲惫是身体在提醒你要照顾好自己。",
        ],
        "carers": [
            "好好睡一觉，明天会好一些的。",
            "记得给自己一些放松的时间。",
            "你值得被好好照顾，包括被你自己。",
        ],
        "closers": [
            "去休息吧，我随时在这里等你。",
            "照顾好自己，别太累了。",
        ]
    },
    "neutral": {
        "openers": [
            "我在呢，想聊点什么？",
            "我在这儿听着呢，你说。",
            "想分享些什么吗？",
        ],
        "explorers": [
            "能多说一点吗？",
            "具体是什么呢？",
            "我想了解更多，你愿意分享吗？",
        ],
        "encouragers": [
            "不管想聊什么，我都在这里。",
            "畅所欲言，我会认真倾听。",
            "你的每一句话我都会认真对待。",
        ],
        "closers": [
            "随时都可以找我聊天。",
            "我随时在这里等你。",
        ]
    }
}


def detect_emotion(text: str) -> Tuple[str, float]:
    """
    检测文本中的具体情绪类型
    返回: (情绪类型, 置信度)
    """
    text_lower = text.lower()
    emotion_scores = {}
    
    # 计算每种情绪的得分
    for category, emotions in EMOTION_CATEGORIES.items():
        for emotion, config in emotions.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += config["weight"]
            if score > 0:
                emotion_scores[emotion] = score
    
    if not emotion_scores:
        return "neutral", 0.5
    
    # 返回得分最高的情绪
    best_emotion = max(emotion_scores, key=emotion_scores.get)
    confidence = min(0.95, 0.5 + emotion_scores[best_emotion] * 0.2)
    
    return best_emotion, confidence


def generate_empathy_response(emotion: str, user_text: str, stage: str = "full") -> str:
    """
    生成共情回复
    stage: "opener" | "explorer" | "validator" | "supporter" | "closer" | "full"
    """
    templates = EMPATHY_TEMPLATES.get(emotion, EMPATHY_TEMPLATES["neutral"])
    
    if stage == "opener":
        return random.choice(templates.get("openers", ["我在听，你说。"]))
    elif stage == "explorer":
        return random.choice(templates.get("explorers", ["能多说一点吗？"]))
    elif stage == "validator":
        return random.choice(templates.get("validators", ["我理解你的感受。"]))
    elif stage == "supporter":
        return random.choice(templates.get("supporters", ["我会一直陪着你。"]))
    elif stage == "closer":
        return random.choice(templates.get("closers", ["随时找我聊天。"]))
    else:  # full - 组合完整回复
        parts = []
        
        # 开场
        if "openers" in templates:
            parts.append(random.choice(templates["openers"]))
        
        # 探索
        if "explorers" in templates:
            parts.append(random.choice(templates["explorers"]))
        
        # 验证/支持
        if "validators" in templates:
            parts.append(random.choice(templates["validators"]))
        elif "supporters" in templates:
            parts.append(random.choice(templates["supporters"]))
        elif "sharers" in templates:
            parts.append(random.choice(templates["sharers"]))
        
        # 结尾
        if "closers" in templates:
            parts.append(random.choice(templates["closers"]))
        
        return "\n\n".join(parts)


def get_empathy_prompt(emotion: str, confidence: float, user_text: str) -> str:
    """
    生成用于AI模型的共情Prompt
    """
    emotion_chinese = {
        "joy": "喜悦", "gratitude": "感恩", "contentment": "满足", "love": "爱意", "pride": "自豪",
        "sadness": "悲伤", "anger": "愤怒", "anxiety": "焦虑", "loneliness": "孤独", 
        "disappointment": "失望", "fatigue": "疲惫",
        "curiosity": "好奇", "confusion": "困惑", "reflection": "反思", "neutral": "平静"
    }.get(emotion, "中性")
    
    # 获取该情绪的回复策略
    empathy_guide = generate_empathy_response(emotion, user_text, stage="full")
    
    prompt = f"""【系统提示 - 情感陪伴模式】
用户当前情绪状态：{emotion_chinese}（置信度：{confidence:.0%}）

【共情指导】
{empathy_guide}

【回复原则】
1. 优先接纳用户的情绪，不要急于给建议或解决方案
2. 用温暖、真诚的语气，像朋友一样对话
3. 适当使用emoji增加亲切感
4. 让用户感到被理解、被接纳、不孤单
5. 回复要简洁自然，不要太长

用户说：{user_text}"""
    
    return prompt


def analyze_and_respond(user_text: str) -> Dict:
    """
    分析用户情绪并生成回复策略
    返回完整的情绪分析结果和回复建议
    """
    # 检测情绪
    emotion, confidence = detect_emotion(user_text)
    
    # 生成共情回复
    empathy_response = generate_empathy_response(emotion, user_text, stage="full")
    
    # 生成AI Prompt
    ai_prompt = get_empathy_prompt(emotion, confidence, user_text)
    
    return {
        "emotion": emotion,
        "emotion_chinese": {
            "joy": "喜悦", "gratitude": "感恩", "contentment": "满足", "love": "爱意", "pride": "自豪",
            "sadness": "悲伤", "anger": "愤怒", "anxiety": "焦虑", "loneliness": "孤独", 
            "disappointment": "失望", "fatigue": "疲惫",
            "curiosity": "好奇", "confusion": "困惑", "reflection": "反思", "neutral": "平静"
        }.get(emotion, "中性"),
        "confidence": confidence,
        "empathy_response": empathy_response,
        "ai_prompt": ai_prompt,
        "category": "positive" if emotion in EMOTION_CATEGORIES["positive"] else 
                   "negative" if emotion in EMOTION_CATEGORIES["negative"] else "neutral"
    }


# 测试
if __name__ == "__main__":
    test_texts = [
        "今天心情超级好，太开心了！",
        "我今天分手了，好难过...",
        "最近工作压力好大，很焦虑",
        "感觉好孤独，没人理解我",
        "真的很生气，他太过分了！",
        "最近太累了，想休息一下"
    ]
    
    for text in test_texts:
        result = analyze_and_respond(text)
        print(f"\n{'='*50}")
        print(f"用户: {text}")
        print(f"情绪: {result['emotion_chinese']} ({result['confidence']:.0%})")
        print(f"分类: {result['category']}")
        print(f"共情回复:\n{result['empathy_response']}")
