import urllib.request
import json

# 测试推荐API
req = urllib.request.Request("http://localhost:8000/recommendations/joy")
try:
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode())
        print("推荐API测试成功:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"错误: {e}")
