import json, os, urllib.request

APP_ID = os.getenv("FEISHU_APP_ID", "your-feishu-app-id")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "your-feishu-app-secret")

token_p = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode()
r = urllib.request.Request("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",data=token_p,headers={"Content-Type":"application/json"},method="POST")
token = json.loads(urllib.request.urlopen(r,timeout=5).read())["tenant_access_token"]
print("Token OK\n")

paths_get = [
    "/open-apis/aily/v1/sessions?page_size=2",
    "/open-apis/aily/v1/knowledge_chunks",
    "/open-apis/aily/v1/knowledge_spaces",
    "/open-apis/aily/v1/apps?page_size=5",
]

paths_post = {
    "/open-apis/aily/v1/sessions": {"skill_id": "default"},
    "/open-apis/aily/v1/ai/chat": {"messages": [{"role":"user","content":"hello"}]},
    "/open-apis/aily/v1/embeddings": {"model":"embedding-001","input":["test"]},
}

for p in paths_get:
    try:
        req = urllib.request.Request(f"https://open.feishu.cn{p}",headers={"Authorization":f"Bearer {token}"})
        d = json.loads(urllib.request.urlopen(req,timeout=5).read())
        print(f"GET  {p}: code={d.get('code')}, msg={d.get('msg','')[:60]}")
    except Exception as e:
        code = getattr(e,"code","?")
        body = ""
        if hasattr(e,"read"):
            try: body = e.read().decode()[:150]
            except: pass
        print(f"GET  {p}: HTTP {code} {body[:120]}")

for p, body_data in paths_post.items():
    try:
        payload = json.dumps(body_data).encode()
        req = urllib.request.Request(f"https://open.feishu.cn{p}",data=payload,headers={"Content-Type":"application/json","Authorization":f"Bearer {token}"},method="POST")
        d = json.loads(urllib.request.urlopen(req,timeout=10).read())
        print(f"POST {p}: code={d.get('code')}, msg={d.get('msg','')[:60]}")
    except Exception as e:
        code = getattr(e,"code","?")
        body = ""
        if hasattr(e,"read"):
            try: body = e.read().decode()[:150]
            except: pass
        print(f"POST {p}: HTTP {code} {body[:120]}")

# Also test old ai paths one more time with new permissions
print("\n--- Old AI paths with new permissions ---")
for p in ["/open-apis/ai/v1/embeddings","/open-apis/ai/v1/chat/completions"]:
    try:
        payload = json.dumps({"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"hi"}],"temperature":0} if "chat" in p else {"model":"embedding-001","input":["test"]}).encode()
        req = urllib.request.Request(f"https://open.feishu.cn{p}",data=payload,headers={"Content-Type":"application/json","Authorization":f"Bearer {token}"},method="POST")
        d = json.loads(urllib.request.urlopen(req,timeout=10).read())
        print(f"POST {p}: code={d.get('code')}, msg={d.get('msg','')[:60]}")
    except Exception as e:
        code = getattr(e,"code","?")
        body = ""
        if hasattr(e,"read"):
            try: body = e.read().decode()[:150]
            except: pass
        print(f"POST {p}: HTTP {code} {body[:120]}")
