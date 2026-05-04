import json, urllib.request as ur, math

BASE = "http://localhost:18080"

def emb(text):
    p = json.dumps({"model":"x","input":[text]}).encode()
    r = ur.Request(f"{BASE}/open-apis/ai/v1/embeddings", data=p,
        headers={"Content-Type":"application/json"}, method="POST")
    return json.loads(ur.urlopen(r, timeout=10).read())["data"]["embeddings"][0]["embedding"]

tests = [
    ("Docker磁盘", "Docker build failed: no space left on device, cannot write image layer"),
    ("GitLab OOM", "GitLab CI Runner job failed with exit code 137, container was killed by OOM killer"),
    ("微服务503", "Spring Cloud Gateway returned 503 Service Unavailable for service user-center"),
    ("Java OOM", "java.lang.OutOfMemoryError: Java heap space at com.example.service.DataProcessor.process"),
]

chunks = [
    ("容器-C1", "Docker 容器部署与 CI/CD 流水线排障指南。问题1：Docker 构建时出现 no space left on device 错误。解决方案：执行 docker system prune -a 清理未使用的镜像和容器，检查磁盘空间 df -h，清理 Docker 构建缓存 docker builder prune。问题2：GitLab CI Runner 报错 ERROR: Job failed: exit code 137。原因通常是 OOM Out of Memory，容器内存不足被内核杀死。解决方案：在 .gitlab-ci.yml 中增加 memory 限制，或升级 Runner 配置。问题3：Kubernetes Pod 一直处于 CrashLoopBackOff 状态。排查步骤：kubectl describe pod 查看事件"),
    ("容器-C2", "冲突。解决：docker network prune 清理未使用的网络，或自定义 network 名称。问题5：Jenkins Pipeline 构建 Docker 镜像时权限不足。在 Jenkinsfile 中添加 docker.withRegistry 和 docker.build 时需要配置 Docker daemon 权限，将 jenkins 用户加入 docker 组：sudo usermod -aG docker jenkins"),
    ("微服务-C1", "微服务架构常见异常排查手册。问题1：Spring Cloud Gateway 出现 503 Service Unavailable 错误。原因通常是目标服务未在注册中心正确注册，或服务实例全部下线。解决方案：检查 Eureka/Nacos 控制台确认服务状态，确认服务 health check 端点正常返回 200。问题2：微服务间调用 Feign 超时 Read timed out。在 application.yml 中增加 feign.client.config.default.connectTimeout 和 readTimeout 配置"),
    ("微服务-C2", "ata.source-proxy-mode: AT。问题4：Nacos 配置中心无法动态刷新配置。确认类上加了 @RefreshScope 注解，且 bootstrap.yml 中 spring.cloud.nacos.config.refresh-enabled 为 true。问题5：消息队列 RocketMQ 消费者重复消费。设置消费者 group 的 consumeMode 为 CLUSTERING，并确保消息处理逻辑幂等"),
    ("开发环境-C1", "内部开发环境踩坑指南。问题1：本地启动微服务报错 java.lang.OutOfMemoryError: Java heap space。解决方案：在 IDE 的 VM options 中增加 -Xmx2048m -Xms512m，或者在 Maven/Gradle 配置中增加 JVM 参数。问题2：Maven 依赖冲突导致 NoSuchMethodError。使用 mvn dependency:tree 查看依赖树，在 pom.xml 中使用 <exclusions> 排除冲突的传递依赖"),
    ("开发环境-C2", "配置。问题3：npm install 报错 EACCES permission denied。解决方案：使用 sudo npm install 或修改 npm 全局目录权限 npm config set prefix ~/.npm-global。问题4：Git pre-commit hook 报错 ESLint 检查不通过。执行 npx eslint --fix src/ 自动修复。问题5：本地 hosts 配置导致服务间调用不通"),
]

for tname, ttext in tests:
    te = emb(ttext)
    tn = math.sqrt(sum(x*x for x in te))
    print(f"\n--- {tname}: {ttext[:60]}... ---")
    best_sim = 0
    best_chunk = ""
    for cname, ctext in chunks:
        ce = emb(ctext)
        cn = math.sqrt(sum(x*x for x in ce))
        cos = sum(a*b for a,b in zip(te,ce)) / (tn*cn)
        if cos > best_sim:
            best_sim = cos
            best_chunk = cname
        if cos > 0.5:
            print(f"  {cname}: cos_sim={cos:.4f}")
    print(f"  Best: {best_chunk} @ cos_sim={best_sim:.4f}")
    print(f"  Result: {'RAG' if best_sim >= 0.6 else '降级'}")
