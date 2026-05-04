import json, os, urllib.request

APP_ID = os.getenv("FEISHU_APP_ID", "your-feishu-app-id")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "your-feishu-app-secret")

token_p = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
r = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",data=token_p,headers={"Content-Type":"application/json"},method="POST")
token = json.loads(urllib.request.urlopen(r,timeout=5).read())["tenant_access_token"]
print("Token OK")

paths = [
    "/open-apis/aily/v1/apps/embeddings",
    "/open-apis/aily/v1/embeddings/create",
    "/open-apis/aily/v1/ai/embeddings",
    "/open-apis/aily/v1/knowledge/embeddings",
    "/open-apis/ai/v1/embeddings/create",
    "/open-apis/aily/v1/sessions",
    "/open-apis/aily/v1/apps",
    "/open-apis/aily/v1/agents",
]
for p in paths:
    try:
        rr = urllib.request.Request(f"https://open.feishu.cn{p}",headers={"Authorization":f"Bearer {token}"})
        d = urllib.request.urlopen(rr,timeout=5).read().decode()[:300]
        print(f"{p}: {d}")
    except Exception as e:
        code = getattr(e,"code","?")
        body = ""
        if hasattr(e,"read"):
            try:
                body = e.read().decode()[:200]
            except:
                pass
        print(f"{p}: HTTP {code} {body}")
