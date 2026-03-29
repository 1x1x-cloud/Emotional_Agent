import requests

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("测试用户认证和情感日记功能")
print("=" * 60)

# 1. 测试新用户注册
print("\n1. 测试新用户注册")
import random
username = f"user_{random.randint(1000, 9999)}"
register_data = {
    "username": username,
    "password": "test123",
    "email": f"{username}@test.com"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
result = response.json()
print(f"注册结果: {result}")

if result.get("success"):
    user_id = result["user_id"]
    
    # 2. 测试登录
    print("\n2. 测试用户登录")
    login_data = {
        "username": username,
        "password": "test123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    result = response.json()
    print(f"登录结果: {result}")
    
    # 3. 测试情感日记
    print("\n3. 测试情感日记")
    diary_data = {
        "user_id": user_id,
        "date": "2026-03-29",
        "emotion": "joy",
        "intensity": 9,
        "notes": "今天心情特别好！",
        "tags": "开心,愉快"
    }
    response = requests.post(f"{BASE_URL}/diary/save", json=diary_data)
    result = response.json()
    print(f"保存日记结果: {result}")
    
    # 4. 获取日记
    response = requests.get(f"{BASE_URL}/diary/{user_id}?date=2026-03-29")
    result = response.json()
    print(f"获取日记结果: {result}")
    
    # 5. 获取日记列表
    response = requests.get(f"{BASE_URL}/diary/list/{user_id}?days=7")
    result = response.json()
    print(f"获取日记列表结果: {len(result.get('diaries', []))} 条记录")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
