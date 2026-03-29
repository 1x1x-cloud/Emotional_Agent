from fastapi import FastAPI  # type: ignore[import]
from pydantic import BaseModel  # type: ignore[import]
from dotenv import load_dotenv  # type: ignore[import]
from fastapi.middleware.cors import CORSMiddleware
# 导入百度SDK
from aip import AipNlp
import os
import httpx  # type: ignore[import]

# 导入共情回复策略
from empathy_strategy import analyze_and_respond, detect_emotion

# 导入数据库操作
from database import init_database, create_conversation, save_message, get_user_conversations, get_conversation_messages, get_user_sentiment_trend, get_daily_sentiment_summary, create_user, get_user_by_username, update_user_last_active, save_emotion_diary, get_emotion_diary, get_emotion_diary_list

# 导入密码哈希
import hashlib
import uuid

# 导入用户画像分析
from user_profile import analyze_user_profile, analyze_emotion_trend, get_emotion_summary

# 导入情感监测与干预
from emotion_monitor import add_emotion_record, check_emotion_alert, get_intervention_suggestion, get_emotion_trend, reset_emotion_monitor

# 导入语音服务
from voice_service import speech_to_text, text_to_speech

# 导入智能推荐服务
from recommendation_service import get_recommendations

app = FastAPI()

# 初始化数据库
init_database()
print("数据库初始化完成")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# 添加CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/hello")
def hello():
    return {"text": "你好，我是后端，已经运行成功啦！"}


# ==================== 用户认证API ====================

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str = None


class LoginRequest(BaseModel):
    username: str
    password: str


def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


@app.post("/auth/register")
async def register(req: RegisterRequest):
    """
    用户注册
    """
    # 检查用户名是否已存在
    existing_user = get_user_by_username(req.username)
    if existing_user:
        return {"success": False, "message": "用户名已存在"}
    
    # 生成用户ID
    user_id = str(uuid.uuid4())
    
    # 创建用户
    password_hash = hash_password(req.password)
    success = create_user(user_id, req.username, password_hash, req.email)
    
    if success:
        return {
            "success": True, 
            "message": "注册成功",
            "user_id": user_id,
            "username": req.username
        }
    else:
        return {"success": False, "message": "注册失败"}


@app.post("/auth/login")
async def login(req: LoginRequest):
    """
    用户登录
    """
    # 获取用户信息
    user = get_user_by_username(req.username)
    if not user:
        return {"success": False, "message": "用户名或密码错误"}
    
    # 验证密码
    password_hash = hash_password(req.password)
    if user["password_hash"] != password_hash:
        return {"success": False, "message": "用户名或密码错误"}
    
    # 更新最后活跃时间
    update_user_last_active(user["id"])
    
    return {
        "success": True,
        "message": "登录成功",
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"]
    }


# ==================== 情感日记API ====================

class EmotionDiaryRequest(BaseModel):
    user_id: str
    date: str
    emotion: str
    intensity: int
    notes: str = None
    tags: str = None


@app.post("/diary/save")
async def save_diary(req: EmotionDiaryRequest):
    """
    保存情感日记
    """
    success = save_emotion_diary(
        req.user_id, req.date, req.emotion, req.intensity, req.notes, req.tags
    )
    
    if success:
        return {"success": True, "message": "日记保存成功"}
    else:
        return {"success": False, "message": "日记保存失败"}


@app.get("/diary/{user_id}")
async def get_diary(user_id: str, date: str = None):
    """
    获取情感日记
    """
    diary = get_emotion_diary(user_id, date)
    return {"success": True, "diary": diary}


@app.get("/diary/list/{user_id}")
async def get_diary_list(user_id: str, days: int = 30):
    """
    获取情感日记列表
    """
    diaries = get_emotion_diary_list(user_id, days)
    return {"success": True, "diaries": diaries}


# ==================== 语音API ====================

from fastapi import File, UploadFile


@app.post("/voice/speech-to-text")
async def voice_to_text(audio: UploadFile = File(...)):
    """
    语音识别：将语音转换为文字
    """
    try:
        audio_data = await audio.read()
        result = speech_to_text(audio_data)
        return result
    except Exception as e:
        return {"success": False, "text": "", "error": str(e)}


@app.post("/voice/text-to-speech")
async def voice_text_to_speech(text: str, spd: int = 5, pit: int = 5, vol: int = 5, per: int = 0):
    """
    语音合成：将文字转换为语音
    """
    try:
        result = text_to_speech(text, spd, pit, vol, per)
        if result["success"]:
            # 返回音频数据（Base64编码）
            import base64
            audio_base64 = base64.b64encode(result["audio_data"]).decode('utf-8')
            return {
                "success": True,
                "audio_base64": audio_base64,
                "format": "mp3"
            }
        else:
            return {"success": False, "error": result["error"]}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== 智能推荐API ====================

@app.get("/recommendations/{emotion}")
async def get_emotion_recommendations(emotion: str):
    """
    获取基于情绪的智能推荐
    """
    try:
        recommendations = get_recommendations(emotion)
        return {"success": True, "recommendations": recommendations}
    except Exception as e:
        return {"success": False, "error": str(e)}


# 初始化百度情感分析客户端
def get_baidu_nlp_client():
    return AipNlp(
        os.getenv("BAIDU_APP_ID"),
        os.getenv("BAIDU_API_KEY"),
        os.getenv("BAIDU_SECRET_KEY")
    )

async def analyze_sentiment(text: str) -> dict:
    """
    百度情感分析 - 优化版本
    结合百度API结果和关键词辅助判断
    """
    try:
        client = get_baidu_nlp_client()
        
        # 调用百度情感分析API
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        
        result = client.sentimentClassify(text)
        
        print(f"[DEBUG] 输入文本: {text}")
        print(f"[DEBUG] 百度API返回结果: {result}")
        
        # 解析结果
        if 'items' in result and result['items']:
            item = result['items'][0]
            sentiment = item.get('sentiment', 0)
            confidence = item.get('confidence', 0)
            positive_prob = item.get('positive_prob', 0)
            negative_prob = item.get('negative_prob', 0)
            
            print(f"[DEBUG] sentiment: {sentiment}, confidence: {confidence}")
            print(f"[DEBUG] positive_prob: {positive_prob}, negative_prob: {negative_prob}")
            
            # 关键词辅助判断
            keyword_sentiment = analyze_sentiment_by_keywords(text)
            print(f"[DEBUG] 关键词判断: {keyword_sentiment}")
            
            # 综合判断：结合API结果和关键词
            final_sentiment = combine_sentiment_results(
                api_sentiment=sentiment,
                api_positive_prob=positive_prob,
                api_negative_prob=negative_prob,
                keyword_sentiment=keyword_sentiment
            )
            
            return final_sentiment
        else:
            return simple_sentiment_analysis(text)
            
    except Exception as e:
        print(f"百度情感分析错误: {e}")
        return simple_sentiment_analysis(text)

def analyze_sentiment_by_keywords(text: str) -> dict:
    """
    基于关键词的情感分析
    返回: {'sentiment': True/False/None, 'confidence': float}
    """
    # 扩展情感词典
    positive_words = [
        "开心", "快乐", "高兴", "喜悦", "幸福", "满足", "兴奋", "棒", "好",
        "很好", "不错", "喜欢", "爱", "赞", "优秀", "完美", "愉快", "舒服",
        "轻松", "自在", "满足", "欣慰", "感动", "温暖", "甜蜜", "美好"
    ]
    
    negative_words = [
        "难过", "悲伤", "痛苦", "焦虑", "愤怒", "失望", "沮丧", "累", "烦",
        "不好", "糟糕", "差", "讨厌", "恨", "伤心", "郁闷", "烦躁", "压抑",
        "孤独", "寂寞", "无助", "绝望", "崩溃", "受不了", "烦死了", "气死了"
    ]
    
    # 计算关键词得分
    text_lower = text.lower()
    positive_score = sum(2 if word in text_lower else 0 for word in positive_words)
    negative_score = sum(2 if word in text_lower else 0 for word in negative_words)
    
    # 考虑否定词
    negation_words = ["不", "没", "无", "别", "不要", "没有"]
    negation_count = sum(1 for word in negation_words if word in text_lower)
    
    # 如果有否定词，可能反转情感
    if negation_count > 0:
        # 简单的否定处理：如果负面词被否定，可能变成正面
        if negative_score > 0:
            negative_score *= 0.5  # 降低负面得分
    
    # 判断结果
    if positive_score > negative_score:
        return {'sentiment': True, 'confidence': min(0.9, 0.5 + positive_score * 0.1)}
    elif negative_score > positive_score:
        return {'sentiment': False, 'confidence': min(0.9, 0.5 + negative_score * 0.1)}
    else:
        return {'sentiment': None, 'confidence': 0.5}

def combine_sentiment_results(api_sentiment, api_positive_prob, api_negative_prob, keyword_sentiment):
    """
    综合API结果和关键词判断
    """
    # 如果API和关键词判断一致，使用API的置信度
    if api_sentiment == 2 and keyword_sentiment['sentiment'] == True:  # 都判断为正向
        return {
            "sentiment": True,
            "label": "正向",
            "confidence": max(api_positive_prob, keyword_sentiment['confidence']),
            "positive": api_positive_prob,
            "negative": api_negative_prob,
            "neutral": 0
        }
    elif api_sentiment == 0 and keyword_sentiment['sentiment'] == False:  # 都判断为负向
        return {
            "sentiment": False,
            "label": "负向",
            "confidence": max(api_negative_prob, keyword_sentiment['confidence']),
            "positive": api_positive_prob,
            "negative": api_negative_prob,
            "neutral": 0
        }
    # 如果不一致，优先使用关键词判断（对于短文本更准确）
    elif keyword_sentiment['sentiment'] is not None:
        if keyword_sentiment['sentiment'] == True:
            return {
                "sentiment": True,
                "label": "正向",
                "confidence": keyword_sentiment['confidence'],
                "positive": api_positive_prob,
                "negative": api_negative_prob,
                "neutral": 0
            }
        else:
            return {
                "sentiment": False,
                "label": "负向",
                "confidence": keyword_sentiment['confidence'],
                "positive": api_positive_prob,
                "negative": api_negative_prob,
                "neutral": 0
            }
    # 默认使用API结果
    else:
        if api_sentiment == 2:
            return {
                "sentiment": True,
                "label": "正向",
                "confidence": api_positive_prob,
                "positive": api_positive_prob,
                "negative": api_negative_prob,
                "neutral": 0
            }
        elif api_sentiment == 0:
            return {
                "sentiment": False,
                "label": "负向",
                "confidence": api_negative_prob,
                "positive": api_positive_prob,
                "negative": api_negative_prob,
                "neutral": 0
            }
        else:
            return {
                "sentiment": None,
                "label": "中性",
                "confidence": 0.5,
                "positive": api_positive_prob,
                "negative": api_negative_prob,
                "neutral": 0.4
            }

def simple_sentiment_analysis(text: str) -> dict:
    """
    本地简单情感分析（降级方案）
    """
    positive_words = ["开心", "快乐", "高兴", "喜悦", "幸福", "满足", "兴奋", "棒", "好", "哈哈", "嘻嘻", "呵呵", "周末", "假期", "舒服", "放松", "惬意"]
    negative_words = ["难过", "悲伤", "痛苦", "焦虑", "愤怒", "失望", "沮丧", "累", "烦"]
    
    positive_score = sum(1 for word in positive_words if word in text)
    negative_score = sum(1 for word in negative_words if word in text)
    
    if positive_score > negative_score:
        return {
            "sentiment": True,
            "label": "正向",
            "confidence": 0.7,
            "positive": 0.7,
            "negative": 0.2,
            "neutral": 0.1
        }
    elif negative_score > positive_score:
        return {
            "sentiment": False,
            "label": "负向",
            "confidence": 0.7,
            "positive": 0.2,
            "negative": 0.7,
            "neutral": 0.1
        }
    else:
        return {
            "sentiment": None,
            "label": "中性",
            "confidence": 0.5,
            "positive": 0.3,
            "negative": 0.3,
            "neutral": 0.4
        }

class SentimentRequest(BaseModel):
    text: str

@app.post("/sentiment")
async def sentiment_analysis(req: SentimentRequest):
    result = await analyze_sentiment(req.text)
    return result


# 数据库相关API
@app.get("/conversations/{user_id}")
async def get_conversations(user_id: str):
    """
    获取用户的所有会话
    """
    conversations = get_user_conversations(user_id)
    return {"conversations": conversations}


@app.get("/messages/{conversation_id}")
async def get_messages(conversation_id: str):
    """
    获取会话的所有消息
    """
    messages = get_conversation_messages(conversation_id)
    return {"messages": messages}


@app.get("/sentiment/trend/{user_id}")
async def get_sentiment_trend(user_id: str, days: int = 7):
    """
    获取用户的情感趋势
    """
    trend = get_user_sentiment_trend(user_id, days)
    return {"trend": trend}


@app.get("/sentiment/summary/{user_id}")
async def get_sentiment_summary_api(user_id: str, days: int = 7):
    """
    获取用户的每日情感总结
    """
    summary = get_daily_sentiment_summary(user_id, days)
    return {"summary": summary}


# 用户画像与情感趋势分析API
@app.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """
    获取用户画像
    """
    conversations = get_user_conversations(user_id)
    all_messages = []
    
    for conv in conversations:
        messages = get_conversation_messages(conv["id"])
        all_messages.extend(messages)
    
    # 只分析用户消息
    user_messages = [msg for msg in all_messages if msg.get("role") == "user"]
    
    profile = analyze_user_profile(user_messages)
    return {"profile": profile}


@app.get("/profile/trend/{user_id}")
async def get_profile_trend(user_id: str, days: int = 7):
    """
    获取用户的情感趋势分析
    """
    conversations = get_user_conversations(user_id)
    all_messages = []
    
    for conv in conversations:
        messages = get_conversation_messages(conv["id"])
        all_messages.extend(messages)
    
    # 只分析用户消息
    user_messages = [msg for msg in all_messages if msg.get("role") == "user"]
    
    # 过滤最近N天的消息
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_messages = []
    
    for msg in user_messages:
        timestamp = msg.get("timestamp", "")
        if timestamp:
            try:
                msg_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
                if msg_date >= cutoff_date:
                    recent_messages.append(msg)
            except:
                pass
    
    trend = analyze_emotion_trend(recent_messages, days)
    return {"trend": trend}


# 情感监测与干预API
@app.get("/emotion/monitor/{user_id}")
async def get_emotion_monitor(user_id: str):
    """
    获取用户的情感监测状态
    """
    trend = get_emotion_trend(user_id)
    alert = check_emotion_alert(user_id)
    suggestion = get_intervention_suggestion(user_id)
    
    return {
        "trend": trend,
        "alert": alert,
        "suggestion": suggestion
    }


@app.post("/emotion/reset/{user_id}")
async def reset_emotion_monitor_api(user_id: str):
    """
    重置情感监测
    """
    reset_emotion_monitor(user_id)
    return {"message": "情感监测已重置"}

class ChatRequest(BaseModel):
    text: str
    user_id: str | None = None
    conversation_id: str | None = None


async def _call_coze_simple(user_text: str, *, user_id: str, conversation_id: str | None) -> str:
    """
    Coze API 调用 - 使用官方 SDK
    """
    print("=== 开始 Coze API 调用 (使用官方 SDK) ===")
    
    # 直接使用用户提供的API密钥和Bot ID进行测试
    api_token = 'pat_GtMXG9FPhRKEdloCdNiuxkQ9rIhA298Qx7jvzB8l5vNO49RDrqW1eCjSLVXM1uhE'
    bot_id = '7618616714799972415'
    
    try:
        # 导入Coze SDK
        from cozepy import Coze, TokenAuth, Message, ChatStatus, MessageContentType, ChatEventType, COZE_CN_BASE_URL
        
        # 初始化Coze客户端
        coze = Coze(auth=TokenAuth(token=api_token), base_url=COZE_CN_BASE_URL)
        
        print(f"API Token: {api_token[:10]}...")
        print(f"Bot ID: {bot_id}")
        print("====================")
        
        # 测试聊天
        print(f"发送消息: {user_text}")
        
        # 收集完整回复
        full_reply = ""
        for event in coze.chat.stream(
            bot_id=bot_id,
            user_id=str(user_id),
            additional_messages=[
                Message.build_user_question_text(user_text),
            ],
        ):
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                print(event.message.content, end="", flush=True)
                full_reply += event.message.content
            
            if event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
                print()
                print("token usage:", event.chat.usage.token_count)
                print("测试成功！")
                break
        
        if full_reply.strip():
            return full_reply.strip()
        else:
            raise Exception("未收到Coze的回复")
            
    except Exception as e:
        print(f"异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise


async def _call_coze_v2(user_text: str, *, user_id: str, conversation_id: str | None) -> str:
    """
    Coze OpenAPI v2 - 使用官方文档格式：/open_api/v2/chat
    """
    api_base = os.getenv("COZE_API_BASE", "https://api.coze.cn").rstrip("/")
    url = f"{api_base}/open_api/v2/chat"
    
    headers = {
        "Authorization": f"Bearer {os.environ['COZE_API_KEY']}",
        "Content-Type": "application/json",
    }
    
    # 修复 v2 API 请求格式
    payload = {
        "bot_id": str(os.environ["COZE_BOT_ID"]),
        "user_id": str(user_id),
        "query": user_text
    }
    
    # 如果有 conversation_id，添加它
    if conversation_id:
        payload["conversation_id"] = str(conversation_id)
    
    print(f"[DEBUG] v2 请求 URL: {url}")
    print(f"[DEBUG] v2 请求体: {payload}")
    
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=payload)
        data = r.json()
        
        print(f"[DEBUG Coze v2] 返回数据: {data}")
        
        # 检查错误码
        if data.get("code") and data.get("code") != 0:
            error_msg = f"Coze API 错误 {data.get('code')}: {data.get('msg')}"
            print(f"[ERROR] {error_msg}")
            raise Exception(error_msg)
        
        # 解析回复 - 根据官方文档，回复可能在 messages 数组中
        msgs = data.get("messages")
        if isinstance(msgs, list) and msgs:
            # 从后往前找最后一条 assistant 消息
            for msg in reversed(msgs):
                if isinstance(msg, dict):
                    role = msg.get("role", "").lower()
                    if role in ("assistant", "bot", "ai"):
                        content = msg.get("content") or msg.get("text")
                        if isinstance(content, str) and content.strip():
                            return content.strip()
            # 如果没找到 role，取最后一条
            last = msgs[-1]
            if isinstance(last, dict):
                content = last.get("content") or last.get("text")
                if isinstance(content, str) and content.strip():
                    return content.strip()
        
        # 尝试其他可能的字段
        for k in ("answer", "reply", "text", "content", "message"):
            v = data.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        
        # 如果都找不到，返回错误信息
        raise Exception(f"无法从 Coze v2 响应中提取回复。响应: {data}")


@app.post("/chat")
async def chat(req: ChatRequest):
    user_text = req.text.strip()
    if not user_text:
        return {"reply": "我在呢。你想聊点什么？"}

    user_id = (req.user_id or "demo_user").strip() or "demo_user"
    conversation_id = (req.conversation_id or "").strip() or None

    print("=== 收到聊天请求 ===")
    print(f"text: '{user_text}'")
    print(f"user_id: '{user_id}'")
    print(f"conversation_id: '{conversation_id}'")
    print(f"COZE_API_KEY: {'已配置' if os.getenv('COZE_API_KEY') else '未配置'}")
    print(f"COZE_BOT_ID: {'已配置' if os.getenv('COZE_BOT_ID') else '未配置'}")
    print(f"COZE_API_BASE: {os.getenv('COZE_API_BASE')}")
    print("===================")

    # 1. 使用共情策略进行情绪分析
    empathy_result = analyze_and_respond(user_text)
    print(f"[DEBUG] 共情分析结果: {empathy_result}")

    # 2. 确保会话存在
    conversation_id = create_conversation(user_id, conversation_id)
    print(f"[DEBUG] 会话ID: {conversation_id}")

    # 3. 保存用户消息到数据库
    user_sentiment = {
        "sentiment": empathy_result["category"] == "positive",
        "label": empathy_result["emotion_chinese"],
        "confidence": empathy_result["confidence"],
        "emotion": empathy_result["emotion"],
        "category": empathy_result["category"]
    }
    save_message(conversation_id, "user", user_text, user_sentiment)
    print(f"[DEBUG] 用户消息已保存")

    # 4. 添加情感记录到监测器
    add_emotion_record(
        user_id,
        empathy_result["emotion"],
        empathy_result["category"] == "positive",
        empathy_result["confidence"]
    )
    print(f"[DEBUG] 情感记录已添加")

    # 5. 检查情绪预警
    alert = check_emotion_alert(user_id)
    print(f"[DEBUG] 情绪预警: {alert}")

    # 6. 获取AI Prompt（包含详细的共情指导）
    ai_prompt = empathy_result["ai_prompt"]
    print(f"[DEBUG] AI Prompt已生成")

    # 5. 构建带情绪提示的用户输入
    enhanced_user_text = ai_prompt

    # 6. 生成回复
    reply = ""
    provider = ""
    
    # 优先走 Coze（如果配置了 Key + BotId）
    if os.getenv("COZE_API_KEY") and os.getenv("COZE_BOT_ID"):
        # 使用简单 API 调用
        try:
            print("[DEBUG] 尝试调用 Coze 简单 API")
            reply = await _call_coze_simple(enhanced_user_text, user_id=user_id, conversation_id=conversation_id)
            print(f"[DEBUG] Coze 简单 API 调用成功: {reply[:50]}...")
            provider = "coze_simple"
        except Exception as e:
            error_msg = str(e)
            print(f"[DEBUG] Coze 简单 API 调用异常: {type(e).__name__}: {error_msg}")
            # 使用共情策略生成的回复
            reply = empathy_result["empathy_response"]
            provider = "empathy_strategy"
    else:
        print("[DEBUG] Coze API 配置不完整，使用共情策略回复")
        # 没配置 Coze 时：使用共情策略生成的回复
        reply = empathy_result["empathy_response"]
        provider = "empathy_strategy"

    # 7. 如果有情绪预警，添加干预建议
    if alert:
        intervention_suggestion = get_intervention_suggestion(user_id)
        if intervention_suggestion:
            reply += f"\n\n💡 {alert['message']}\n{intervention_suggestion}"
            print(f"[DEBUG] 添加干预建议")

    # 8. 保存AI回复到数据库
    save_message(conversation_id, "assistant", reply)
    print(f"[DEBUG] AI回复已保存")

    print(f"[DEBUG] 使用{provider}回复: {reply[:50]}...")
    return {
        "reply": reply, 
        "provider": provider, 
        "conversation_id": conversation_id,
        "sentiment": user_sentiment,
        "alert": alert
    }

def generate_mood_prompt(sentiment_result: dict) -> str:
    """
    根据情感分析结果生成情绪提示
    """
    sentiment = sentiment_result.get("sentiment")
    label = sentiment_result.get("label", "中性")
    confidence = sentiment_result.get("confidence", 0.5)
    
    if sentiment is True:  # 正向
        return f"【系统提示】用户当前情绪为{label}（置信度{confidence:.0%}）。请用轻松、愉快、温暖的语气回答，可以分享用户的喜悦，保持积极向上的态度。"
    elif sentiment is False:  # 负向
        return f"【系统提示】用户当前情绪为{label}（置信度{confidence:.0%}）。请用温柔、理解、共情的语气回答，优先倾听和安慰，不要急于给建议，多用'我能理解你'、'我在这里陪着你'这类表达，让用户感到被接纳和支持。"
    else:  # 中性
        return f"【系统提示】用户当前情绪为{label}。请用正常、友好、温和的语气回答，保持开放和接纳的态度。"

def generate_local_reply(user_text: str, sentiment_result: dict) -> str:
    """
    根据情感分析结果生成本地兜底回复
    """
    sentiment = sentiment_result.get("sentiment")
    
    if sentiment is True:  # 正向
        return "听你这么说，我也能感受到你的开心！愿意和我分享一下是什么让你这么高兴吗？"
    elif sentiment is False:  # 负向
        return "我能感受到你现在可能不太好受。愿意的话，可以和我多说一点，我一直在这里陪着你。"
    else:  # 中性
        return "我在呢。你想聊点什么都可以，我会一直陪着你。"