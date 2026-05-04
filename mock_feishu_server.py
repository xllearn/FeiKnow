import json
import hashlib
import struct
import math
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 18080

TECH_KEYWORDS = [
    "docker", "container", "kubernetes", "pod", "deployment", "image", "build",
    "gitlab", "ci", "cd", "pipeline", "runner", "jenkins", "devops",
    "spring", "cloud", "gateway", "microservice", "eureka", "nacos", "feign",
    "seata", "distributed", "transaction", "rocketmq", "message", "queue",
    "maven", "gradle", "dependency", "npm", "node", "permission",
    "java", "heap", "memory", "outofmemory", "jvm", "oom",
    "network", "crash", "error", "failed", "timeout", "503", "unavailable",
    "eslint", "git", "hosts", "config", "refresh", "restart",
    "dockerfile", "compose", "volume", "disk", "space",
    "log", "debug", "trace", "stack", "exception",
]

def text_to_keyword_vector(text, dims=1024):
    text_lower = text.lower()
    vec = [0.0] * dims
    
    for i, kw in enumerate(TECH_KEYWORDS):
        if i >= dims:
            break
        pattern = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
        if pattern.search(text_lower):
            vec[i] = 1.0
    
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    
    return vec


class MockFeishuHandler(BaseHTTPRequestHandler):
    
    def _send_json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _keyword_match_response(self, messages):
        system_text = ""
        user_text = ""
        for m in messages:
            if m.get("role") == "system":
                system_text = m.get("content", "")
            elif m.get("role") == "user":
                user_text = m.get("content", "")

        combined = (user_text + " " + system_text).lower()

        if "docker" in combined and ("space" in combined or "no space" in combined):
            return "执行 docker system prune -a 清理未使用的镜像和容器，然后 df -h 检查磁盘空间。"
        elif "docker" in combined and "build" in combined:
            return "使用 docker builder prune 清理构建缓存，再重新构建镜像。"
        elif "docker" in combined and ("permission" in combined or "daemon" in combined):
            return "执行 sudo usermod -aG docker jenkins 将用户加入 docker 组，然后重新登录终端。"
        elif ("gitlab" in combined or "ci" in combined) and ("137" in combined or "oom" in combined or "killed" in combined):
            return "在 .gitlab-ci.yml 中增加 memory 限制到 4GB，或升级 GitLab Runner 的硬件配置。"
        elif "kubernetes" in combined or "crashloopbackoff" in combined or ("pod" in combined and "crash" in combined):
            return "执行 kubectl describe pod <pod-name> 查看事件日志，kubectl logs <pod-name> --previous 查看崩溃前日志。"
        elif "docker" in combined and "network" in combined:
            return "执行 docker network prune 清理未使用的网络，或为 docker-compose 中 service 指定自定义网络名称。"
        elif "503" in combined and ("gateway" in combined or "unavailable" in combined):
            return "检查 Eureka/Nacos 控制台确认目标服务是否已注册且健康检查通过。"
        elif "feign" in combined and ("timeout" in combined or "timed" in combined):
            return "在 application.yml 中增加 feign.client.config.default.connectTimeout=5000 和 readTimeout=30000，配合 Sentinel 熔断降级。"
        elif "seata" in combined or "undo_log" in combined:
            return "确保每个业务库都创建了 undo_log 表，并在配置中设置 seata.data-source-proxy-mode: AT。"
        elif "nacos" in combined and ("refresh" in combined or "刷新" in combined):
            return "在类上添加 @RefreshScope 注解，并确认 bootstrap.yml 中配置 nacos.config.refresh-enabled: true。"
        elif "rocketmq" in combined or ("消息" in combined and ("重复" in combined or "消费" in combined)):
            return "设置消费者 group 的 consumeMode 为 CLUSTERING，并通过数据库唯一键+Redis 实现消息幂等处理。"
        elif "outofmemoryerror" in combined or "heap space" in combined or ("java" in combined and "heap" in combined):
            return "在 IDE 的 VM options 中增加 -Xmx2048m -Xms512m 参数以分配更多堆内存，或优化代码减少对象创建。"
        elif "maven" in combined and ("conflict" in combined or "nosuchmethod" in combined):
            return "使用 mvn dependency:tree 查看依赖树，在 pom.xml 中用 <exclusions> 排除冲突的传递依赖。"
        elif "npm" in combined and ("permission" in combined or "eacces" in combined):
            return "使用 sudo npm install 或执行 npm config set prefix ~/.npm-global 修改全局目录权限。"
        elif "eslint" in combined or ("pre-commit" in combined and ("fail" in combined or "不通过" in combined)):
            return "执行 npx eslint --fix src/ 自动修复代码风格，或在 .eslintrc.js 中调整规则严格度。"
        elif "hosts" in combined and ("不通" in combined or "connect" in combined or "resolve" in combined):
            return "检查 hosts 文件中是否正确配置了服务域名映射，如 127.0.0.1 service-registry.local。"
        elif "indentation" in combined or "syntax" in combined or ("python" in combined and "error" in combined):
            return "检查代码缩进是否一致，Python 要求统一使用空格或 Tab，建议用 IDE 的自动格式化功能修复。"
        else:
            return "建议查看相关日志文件，检查配置文件是否正确，必要时联系运维团队获取进一步帮助。"

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b"{}"
        
        try:
            req = json.loads(body.decode("utf-8"))
        except:
            req = {}

        if "/auth/v3/tenant_access_token/internal" in self.path:
            self._send_json(200, {
                "code": 0,
                "msg": "ok",
                "tenant_access_token": "mock-feishu-token-12345",
                "expire": 7200
            })

        elif "/ai/v1/embeddings" in self.path:
            input_texts = req.get("input", [""])
            embeddings = []
            for text in input_texts:
                vec = text_to_keyword_vector(text)
                embeddings.append({"embedding": vec})
            self._send_json(200, {
                "code": 0,
                "data": {"embeddings": embeddings}
            })

        elif "/ai/v1/chat/completions" in self.path:
            messages = req.get("messages", [])
            reply = self._keyword_match_response(messages)
            self._send_json(200, {
                "code": 0,
                "data": {
                    "choices": [{
                        "message": {"content": reply, "role": "assistant"}
                    }]
                }
            })

        elif "/im/v1/messages" in self.path:
            self._send_json(200, {"code": 0, "msg": "success"})

        else:
            self._send_json(404, {"code": -1, "msg": "not found"})

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), MockFeishuHandler)
    print(f"Mock Feishu API v2 (keyword-vector embeddings) running on port {PORT}")
    server.serve_forever()
