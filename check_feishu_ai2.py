import json, os, urllib.request

APP_ID = os.getenv("FEISHU_APP_ID", "your-feishu-app-id")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "your-feishu-app-secret")

token_p = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
r = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",data=token_p,headers={"Content-Type":"application/json"},method="POST")
token = json.loads(urllib.request.urlopen(r,timeout=5).read())["tenant_access_token"]
print("Token OK")

# Try POST-based queries (not just GET)
tests = {
    "embeddings": {
        "path": "/open-apis/ai/v1/embeddings",
        "body": {"model":"embedding-001","input":["test"]}
    },
    "chat": {
        "path": "/open-apis/ai/v1/chat/completions", 
        "body": {"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"hi"}],"temperature":0}
    },
    "aily_sessions": {
        "path": "/open-apis/aily/v1/sessions",
        "body": {}
    }
}

for name, cfg in tests.items():
    try:
        p = json.dumps(cfg["body"]).encode() if cfg["body"] else None
        req = urllib.request.Request(
            f"https://open.feishu.cn{cfg['path']}",
            data=p,
            headers={"Content-Type":"application/json","Authorization":f"Bearer {token}"},
            method="POST" if p else "GET"
        )
        d = json.loads(urllib.request.urlopen(req, timeout=10).read())
        print(f"{name}: code={d.get('code')}, msg={d.get('msg','')[:100]}")
    except Exception as e:
        code = getattr(e,"code","?")
        body = ""
        if hasattr(e,"read"):
            try: body = e.read().decode()[:200]
            except: pass
        print(f"{name}: HTTP {code} {body}")
