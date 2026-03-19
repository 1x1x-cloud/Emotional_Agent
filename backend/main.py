from fastapi import FastAPI  # type: ignore[import]
from pydantic import BaseModel  # type: ignore[import]
from dotenv import load_dotenv  # type: ignore[import]
import os
import httpx  # type: ignore[import]

app = FastAPI()

load_dotenv()

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/hello")
def hello():
    return {"text": "你好，我是后端，已经运行成功啦！"}


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

    # 优先走 Coze（如果配置了 Key + BotId）
    if os.getenv("COZE_API_KEY") and os.getenv("COZE_BOT_ID"):
        # 使用简单 API 调用
        try:
            print("[DEBUG] 尝试调用 Coze 简单 API")
            reply = await _call_coze_simple(user_text, user_id=user_id, conversation_id=conversation_id)
            print(f"[DEBUG] Coze 简单 API 调用成功: {reply[:50]}...")
            return {"reply": reply, "provider": "coze_simple"}
        except Exception as e:
            error_msg = str(e)
            print(f"[DEBUG] Coze 简单 API 调用异常: {type(e).__name__}: {error_msg}")
            # 暂时返回测试回复，以便服务能够正常运行
            return {
                "reply": "你好！我是测试回复。后端服务运行正常，但Coze API暂时无法连接。",
                "provider": "test"
            }
            # 以下是原来的错误提示，暂时注释掉
            # return {
            #     "reply": "抱歉，AI 服务暂时无法连接。请稍后再试，或检查 Bot 是否已正确发布。",
            #     "provider": "error"
            # }
    else:
        print("[DEBUG] Coze API 配置不完整，使用本地兜底回复")

    # 没配置 Coze 时：本地兜底“共情风格”回复，保证 demo 随时可跑
    low_mood_markers = ("难过", "不开心", "焦虑", "崩溃", "压力", "累", "想哭", "烦", "抑郁")
    if any(k in user_text for k in low_mood_markers):
        reply = "我听到你现在有点不容易。愿意的话，你可以多说一点：是发生了什么，还是这种感觉已经持续了一段时间？"
    else:
        reply = "我在。你愿意和我说说你现在最在意的是什么吗？"

    print(f"[DEBUG] 使用本地兜底回复: {reply[:50]}...")
    return {"reply": reply, "provider": "local_fallback"}