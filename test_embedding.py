import json, os, urllib.request

APP_ID = os.getenv("FEISHU_APP_ID", "your-feishu-app-id")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "your-feishu-app-secret")

# Get token
payload = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
req = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", data=payload, headers={"Content-Type":"application/json"}, method="POST")
resp = json.loads(urllib.request.urlopen(req, timeout=5).read())
token = resp["tenant_access_token"]
print(f"Token obtained: {token[:20]}...")

# Test embedding
payload2 = json.dumps({"model":"embedding-001","input":["Docker container build failed"]}).encode()
req2 = urllib.request.Request(
    "https://open.feishu.cn/open-apis/ai/v1/embeddings",
    data=payload2,
    headers={"Content-Type":"application/json", "Authorization": f"Bearer {token}"},
    method="POST"
)
try:
    resp2 = urllib.request.urlopen(req2, timeout=10)
    data = json.loads(resp2.read().decode())
    print(f"Embedding API code: {data.get('code')}, msg: {data.get('msg')}")
    if data.get("data"):
        emb = data["data"].get("embeddings",[{}])[0].get("embedding",[])
        print(f"Embedding dimensions: {len(emb)}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, "read"):
        print(e.read().decode())
