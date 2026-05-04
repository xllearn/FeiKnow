import json, urllib.request as ur

BASE = "http://localhost:18080"

def get_embedding(text):
    payload = json.dumps({"model":"embedding-001","input":[text]}).encode()
    req = ur.Request(f"{BASE}/open-apis/ai/v1/embeddings",
        data=payload,
        headers={"Content-Type":"application/json"},
        method="POST")
    data = json.loads(ur.urlopen(req, timeout=10).read())
    return data["data"]["embeddings"][0]["embedding"]

# Get document chunk embedding
doc_text = "Docker 容器部署与 CI/CD 流水线排障指南。问题1：Docker 构建时出现 no space left on device 错误。解决方案：执行 docker system prune -a 清理未使用的镜像和容器，检查磁盘空间 df -h，清理 Docker 构建缓存 docker builder prune。"
doc_emb = get_embedding(doc_text)

# Get query embedding
query_text = "Docker build failed: no space left on device"
query_emb = get_embedding(query_text)

# Compute cosine similarity
import math
dot = sum(a*b for a,b in zip(doc_emb, query_emb))
norm_doc = math.sqrt(sum(x*x for x in doc_emb))
norm_query = math.sqrt(sum(x*x for x in query_emb))
cos_sim = dot / (norm_doc * norm_query)
cos_dist = 1 - cos_sim

print(f"Document non-zero dims: {sum(1 for x in doc_emb if abs(x) > 0.001)}")
print(f"Query non-zero dims: {sum(1 for x in query_emb if abs(x) > 0.001)}")
print(f"Cosine similarity: {cos_sim:.6f}")
print(f"Cosine distance (<->): {cos_dist:.6f}")
print(f"1 - distance: {1 - cos_dist:.6f}")
print(f"Threshold: 0.6 -> {'PASS' if 1-cos_dist >= 0.6 else 'FAIL'}")

# Also check: query vs query (same text)
query_emb2 = get_embedding(query_text)
dot2 = sum(a*b for a,b in zip(query_emb, query_emb2))
cos_sim2 = dot2 / (norm_query * norm_query)
print(f"\nSame query cosine sim: {cos_sim2:.6f} (should be 1.0)")
