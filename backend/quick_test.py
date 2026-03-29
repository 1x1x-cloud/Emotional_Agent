import requests

# 测试推荐API
try:
    r = requests.get("http://localhost:8000/recommendations/joy", timeout=5)
    print("推荐API测试:")
    print(r.json())
except Exception as e:
    print(f"错误: {e}")
