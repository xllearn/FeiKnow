import json, urllib.request

def send_webhook(event_id, doc_id, title, content):
    payload = {
        "schema": "2.0",
        "header": {
            "event_id": event_id,
            "event_type": "docx.document.update_v2",
            "create_time": "1680000000000"
        },
        "event": {
            "object": {
                "document": {
                    "doc_id": doc_id,
                    "title": title
                },
                "content": content
            }
        }
    }
    
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        "http://localhost:8080/api/v1/feishu/webhook",
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST"
    )
    
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(f"[{title}] code={result.get('code')}, message={result.get('message')}, data={result.get('data')}")

# 文档1：容器部署与CI流水线排障指南
send_webhook("evt-container-001", "doc-container-guide", "2024 容器部署与CI流水线排障指南",
    "Docker 容器部署与 CI/CD 流水线排障指南。问题1：Docker 构建时出现 no space left on device 错误。"
    "解决方案：执行 docker system prune -a 清理未使用的镜像和容器，检查磁盘空间 df -h，"
    "清理 Docker 构建缓存 docker builder prune。问题2：GitLab CI Runner 报错 ERROR: Job failed: exit code 137。"
    "原因通常是 OOM Out of Memory，容器内存不足被内核杀死。解决方案：在 .gitlab-ci.yml 中增加 memory 限制，"
    "或升级 Runner 配置。问题3：Kubernetes Pod 一直处于 CrashLoopBackOff 状态。"
    "排查步骤：kubectl describe pod 查看事件，kubectl logs pod --previous 查看上一次容器的日志。"
    "问题4：Docker Compose 启动时 network 冲突。解决：docker network prune 清理未使用的网络，"
    "或自定义 network 名称。问题5：Jenkins Pipeline 构建 Docker 镜像时权限不足。"
    "在 Jenkinsfile 中添加 docker.withRegistry 和 docker.build 时需要配置 Docker daemon 权限，"
    "将 jenkins 用户加入 docker 组：sudo usermod -aG docker jenkins"
)

# 文档2：微服务架构常见异常排查手册
send_webhook("evt-micro-002", "doc-microservice-guide", "2024 微服务架构常见异常排查手册",
    "微服务架构常见异常排查手册。问题1：Spring Cloud Gateway 出现 503 Service Unavailable 错误。"
    "原因通常是目标服务未在注册中心正确注册，或服务实例全部下线。解决方案：检查 Eureka/Nacos 控制台确认服务状态，"
    "确认服务 health check 端点正常返回 200。问题2：微服务间调用 Feign 超时 Read timed out。"
    "在 application.yml 中增加 feign.client.config.default.connectTimeout 和 readTimeout 配置，"
    "建议分别设为 5000ms 和 30000ms。同时配合 Hystrix/Sentinel 熔断降级。问题3：分布式事务 Seata AT 模式出现 "
    "branch rollback failed 错误。原因是 undo_log 表未创建或数据源代理未配置。确保每个业务库都创建 undo_log 表，"
    "并在 application.yml 中配置 seata.data-source-proxy-mode: AT。问题4：Nacos 配置中心无法动态刷新配置。"
    "确认类上加了 @RefreshScope 注解，且 bootstrap.yml 中 spring.cloud.nacos.config.refresh-enabled 为 true。"
    "问题5：消息队列 RocketMQ 消费者重复消费。设置消费者 group 的 consumeMode 为 CLUSTERING，"
    "并确保消息处理逻辑幂等，通过数据库唯一键或 Redis 去重实现。"
)

# 文档3：内部开发环境踩坑指南
send_webhook("evt-env-003", "doc-dev-env-guide", "2024 内部开发环境踩坑指南",
    "内部开发环境踩坑指南。问题1：本地启动微服务报错 java.lang.OutOfMemoryError: Java heap space。"
    "解决方案：在 IDE 的 VM options 中增加 -Xmx2048m -Xms512m，或者在 Maven/Gradle 配置中增加 JVM 参数。"
    "问题2：Maven 依赖冲突导致 NoSuchMethodError。使用 mvn dependency:tree 查看依赖树，"
    "在 pom.xml 中使用 <exclusions> 排除冲突的传递依赖，或使用 <dependencyManagement> 统一版本。"
    "问题3：npm install 报错 EACCES permission denied。解决方案：使用 sudo npm install 或修改 npm 全局目录权限 "
    "npm config set prefix ~/.npm-global，或使用 nvm 管理 Node.js 版本避免权限问题。"
    "问题4：Git pre-commit hook 报错 ESLint 检查不通过。执行 npx eslint --fix src/ 自动修复，"
    "或在 .eslintrc.js 中调整规则严格度。问题5：本地 hosts 配置导致服务间调用不通。"
    "检查 C:\\Windows\\System32\\drivers\\etc\\hosts 文件中是否正确配置了服务域名映射，"
    "如 127.0.0.1 service-registry.local。"
)

print("\n全部文档入库完成！")
