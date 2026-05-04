import json, os, urllib.request

API_KEY = os.getenv("AI_API_KEY", "your-api-key-here")
BASE = os.getenv("AI_BASE_URL", "https://api.deepseek.com")

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}

# Test 1: Chat API
try:
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Say hello in one word"}],
        "max_tokens": 10
    }).encode()
    req = urllib.request.Request(f"{BASE}/v1/chat/completions", data=payload, headers=headers, method="POST")
    data = json.loads(urllib.request.urlopen(req, timeout=15).read())
    reply = data["choices"][0]["message"]["content"]
    print(f"Chat API: OK -> '{reply}'")
except Exception as e:
    print(f"Chat API: FAIL - {e}")

# Test 2: Embeddings API
try:
    payload = json.dumps({
        "model": "text-embedding-3-small",
        "input": ["Docker container build error"]
    }).encode()
    req = urllib.request.Request(f"{BASE}/v1/embeddings", data=payload, headers=headers, method="POST")
    data = json.loads(urllib.request.urlopen(req, timeout=15).read())
    dims = len(data["data"][0]["embedding"])
    print(f"Embeddings API: OK -> {dims} dims")
except Exception as e:
    body = ""
    if hasattr(e, "read"):
        try: body = e.read().decode()[:300]
        except: pass
    print(f"Embeddings API: FAIL - {e} {body}")

# Test 3: List models
try:
    req = urllib.request.Request(f"{BASE}/v1/models", headers=headers)
    data = json.loads(urllib.request.urlopen(req, timeout=10).read())
    models = [m["id"] for m in data.get("data", []) if "embed" in m.get("id", "").lower() or "chat" in m.get("id", "").lower()]
    print(f"Available AI models: {models if models else 'No chat/embed models found'}")
except Exception as e:
    print(f"Models API: {e}")
