import json, os, urllib.request

APP_ID = os.getenv("FEISHU_APP_ID", "your-feishu-app-id")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "your-feishu-app-secret")

# Get token
payload = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
req = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", data=payload, headers={"Content-Type":"application/json"}, method="POST")
resp = json.loads(urllib.request.urlopen(req, timeout=5).read())
token = resp["tenant_access_token"]
print(f"Token obtained: OK")

# Test Chat Completion API
payload2 = json.dumps({
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.0
}).encode()
req2 = urllib.request.Request(
    "https://open.feishu.cn/open-apis/ai/v1/chat/completions",
    data=payload2,
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    method="POST"
)
try:
    resp2 = urllib.request.urlopen(req2, timeout=10)
    data = json.loads(resp2.read().decode())
    print(f"Chat API code: {data.get('code')}, msg: {data.get('msg')}")
    if data.get("data"):
        print("Chat API works!")
except Exception as e:
    print(f"Chat API Error: {e}")
    if hasattr(e, "read"):
        print(e.read().decode()[:500])
