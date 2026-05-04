import json, urllib.request

BASE = "http://localhost:8080"

def rescue(error_text, description):
    payload = json.dumps({"errorText": error_text}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}/api/v1/rescue",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            data = result.get("data", "")
            code = result.get("code")
            message = result.get("message", "")
            is_knowledge = not data.startswith("[来自通用大模型]")
            print(f"\n{'='*70}")
            print(f"测试: {description}")
            print(f"输入: {error_text[:100]}")
            print(f"状态: code={code}, message={message}")
            print(f"来源: {'私域知识库 RAG' if is_knowledge else '通用大模型(降级)'}")
            print(f"结果: {data[:400]}")
            print(f"{'='*70}")
            return is_knowledge, data
    except Exception as e:
        print(f"\n测试: {description}")
        print(f"错误: {e}")
        return False, str(e)

print("\n" + "="*70)
print("  FeiKnow RAG 知识库命中测试")
print("  知识库: 容器部署 / 微服务异常 / 开发环境踩坑")
print("="*70)

results = []

# 测试1：Docker 空格不足 → 应命中"容器部署"文档
r1 = rescue("Docker build failed: no space left on device, cannot write image layer",
    "Docker 构建磁盘空间不足 (应命中容器部署指南)")
results.append(("Docker磁盘不足", r1[0]))

# 测试2：GitLab CI OOM → 应命中"容器部署"文档
r2 = rescue("GitLab CI Runner job failed with exit code 137, container was killed by OOM killer",
    "GitLab CI OOM (应命中容器部署指南)")
results.append(("GitLab OOM", r2[0]))

# 测试3：微服务 503 → 应命中"微服务异常"文档
r3 = rescue("Spring Cloud Gateway returned 503 Service Unavailable for service user-center",
    "微服务 Gateway 503 (应命中微服务异常手册)")
results.append(("微服务503", r3[0]))

# 测试4：Java 堆溢出 → 应命中"开发环境"文档
r4 = rescue("java.lang.OutOfMemoryError: Java heap space at com.example.service.DataProcessor.process",
    "Java 堆溢出 (应命中开发环境踩坑指南)")
results.append(("Java OOM", r4[0]))

# 测试5：不相关错误 → 应降级到通用模型
r5 = rescue("Python script failed with IndentationError: unexpected indent at line 42",
    "Python 缩进错误 (应降级到通用大模型)")
results.append(("Python缩进", r5[0]))

# 汇总
print("\n\n" + "="*70)
print("  测试结果汇总")
print("="*70)
for name, hit in results:
    status = "私域RAG命中" if hit else "通用降级"
    icon = "PASS" if (
        (name in ["Docker磁盘不足","GitLab OOM","微服务503","Java OOM"] and hit) or
        (name == "Python缩进" and not hit)
    ) else "FAIL"
    print(f"  [{icon}] {name}: {status}")
print("="*70)
