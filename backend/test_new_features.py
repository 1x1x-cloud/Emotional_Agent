"""
测试新功能
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("测试新功能")
print("=" * 60)

# 1. 测试用户注册
print("\n1. 测试用户注册")
register_data = {
    "username": "test_user",
    "password": "test_password",
    "email": "test@example.com"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print(f"注册结果: {response.json()}")

# 2. 测试用户登录
print("\n2. 测试用户登录")
login_data = {
    "username": "test_user",
    "password": "test_password"
}
response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
login_result = response.json()
print(f"登录结果: {login_result}")

if login_result.get("success"):
    user_id = login_result["user_id"]
    
    # 3. 测试情感日记
    print("\n3. 测试情感日记")
    diary_data = {
        "user_id": user_id,
        "date": "2026-03-29",
        "emotion": "joy",
        "intensity": 8,
        "notes": "今天心情很好，工作顺利！",
        "tags": "工作,顺利"
    }
    response = requests.post(f"{BASE_URL}/diary/save", json=diary_data)
    print(f"保存日记结果: {response.json()}")
    
    # 获取日记
    response = requests.get(f"{BASE_URL}/diary/{user_id}?date=2026-03-29")
    print(f"获取日记结果: {response.json()}")
    
    # 获取日记列表
    response = requests.get(f"{BASE_URL}/diary/list/{user_id}?days=30")
    print(f"获取日记列表结果: {len(response.json().get('diaries', []))} 条记录")

# 4. 测试智能推荐
print("\n4. 测试智能推荐")
emotions = ["joy", "sadness", "anxiety", "anger"]
for emotion in emotions:
    response = requests.get(f"{BASE_URL}/recommendations/{emotion}")
    result = response.json()
    if result.get("success"):
        rec = result["recommendations"]
        print(f"\n{emotion} 推荐:")
        print(f"  消息: {rec['message']}")
        print(f"  音乐: {len(rec['music'])} 首")
        print(f"  文章: {len(rec['articles'])} 篇")
        print(f"  活动: {len(rec['activities'])} 个")

# 5. 测试语音合成（仅测试API是否可用）
print("\n5. 测试语音合成API")
response = requests.post(f"{BASE_URL}/voice/text-to-speech?text=你好，我是情感陪伴AI")
result = response.json()
print(f"语音合成结果: {'成功' if result.get('success') else '失败'}")
if result.get('success'):
    print(f"  音频数据长度: {len(result.get('audio_base64', ''))} 字符")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
