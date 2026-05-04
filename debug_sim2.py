import json, urllib.request as ur, math

BASE = "http://localhost:18080"

def get_embedding(text):
    payload = json.dumps({"model":"embedding-001","input":[text]}).encode()
    req = ur.Request(f"{BASE}/open-apis/ai/v1/embeddings",
        data=payload, headers={"Content-Type":"application/json"}, method="POST")
    data = json.loads(ur.urlopen(req, timeout=10).read())
    return data["data"]["embeddings"][0]["embedding"]

# Get embedding for query
query = "Docker build failed: no space left on device"
q_emb = get_embedding(query)

print("Query:", query)
print(f"Query embedding non-zero dims: {sum(1 for x in q_emb if abs(x) > 0.0001)}")
print()

# Check against each chunk in the database
for i, doc_text in enumerate([
    "Docker 容器部署与 CI/CD 流水线排障指南。问题1：Docker 构建时出现 no space left on device 错误。解决方案：执行 docker system prune -a 清理未使用的镜像和容器，检查磁盘空间 df -h，清理 Docker 构建缓存 docker builder prune。问题2：GitLab CI Runner 报错 ERROR: Job failed: exit code 137。原因通常是 OOM Out of Memory，容器内存不足被内核杀死。解决方案：在 .gitlab-ci.yml 中增加 memory 限制，或升级 Runner 配置。问题3：Kubernetes Pod 一直处于 CrashLoopBackOff 状态。排查步骤：kubectl describe pod 查看事件",
    "冲突。解决：docker network prune 清理未使用的网络，或自定义 network 名称。问题5：Jenkins Pipeline 构建 Docker 镜像时权限不足。在 Jenkinsfile 中添加 docker.withRegistry 和 docker.build 时需要配置 Docker daemon 权限，将 jenkins 用户加入 docker 组：sudo usermod -aG docker jenkins",
]):
    d_emb = get_embedding(doc_text)
    dot = sum(a*b for a,b in zip(q_emb, d_emb))
    nq = math.sqrt(sum(x*x for x in q_emb))
    nd = math.sqrt(sum(x*x for x in d_emb))
    sim = dot / (nq * nd)
    dist = 1 - sim
    print(f"Chunk {i+1}: sim={sim:.6f}, dist={dist:.6f}, codestr 1-dist={1-dist:.6f}, hit={'YES' if 1-dist>=0.6 else 'NO'}")
    print(f"  Preview: {doc_text[:80]}...")
    print()
