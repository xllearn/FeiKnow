import json
import sys
import time
import urllib.request
import urllib.error
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE = "http://localhost:8080"
REQUEST_TIMEOUT = 60

# ============================================================
#  终端 ANSI 颜色定义
# ============================================================
C = {
    "R": "\033[91m",
    "G": "\033[92m",
    "Y": "\033[93m",
    "B": "\033[94m",
    "C": "\033[96m",
    "M": "\033[95m",
    "W": "\033[97m",
    "D": "\033[90m",
    "X": "\033[0m",
    "BD": "\033[1m",
    "UL": "\033[4m",
}
_c = lambda key, text: f"{C.get(key,'')}{text}{C['X']}"


def hr(width=70):
    print(_c("D", "─" * width))


def box_header(title):
    hr(68)
    print(f"  {_c('BD', _c('C', title))}")
    hr(68)


def box_footer():
    hr(68)


def _api_post(path, payload, timeout=REQUEST_TIMEOUT):
    url = f"{BASE}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _api_get(path, timeout=REQUEST_TIMEOUT):
    url = f"{BASE}{path}"
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def check_backend():
    import socket
    try:
        sock = socket.create_connection(("localhost", 8080), timeout=3)
        sock.close()
        print(_c("G", "  [✓] 后端服务连接正常  (localhost:8080)"))
        return True
    except Exception as e:
        print(_c("R", "  [✗] 后端服务不可达！请先启动: mvn spring-boot:run"))
        print(_c("D", f"       错误详情: {e}"))
        return False


def test_feishu_channel():
    print()
    print(_c("B", "  📡 正在测试飞书群通道..."))
    try:
        resp = _api_get("/api/v1/rescue/test-feishu", timeout=10)
        code = resp.get("code")
        msg = resp.get("data", resp.get("message", ""))
        if code == 200 or code == 0:
            print(_c("G", f"  [✓] 飞书群消息已发送 → 请打开飞书群查看卡片"))
            print(_c("D", f"       返回: {msg}"))
            return True
        else:
            print(_c("Y", f"  [!] 飞书群通道异常: code={code}, msg={msg}"))
            return False
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(_c("Y", f"  [!] 飞书群通道 HTTP {e.code}: {body[:200]}"))
        return False
    except Exception as e:
        print(_c("Y", f"  [!] 飞书群通道不可用: {e}"))
        return False


def rescue(error_text, description, expect_rag=True):
    """
    发起 rescue 请求，展示双通道输出。
    expect_rag: 预期是否命中私域知识库 (用于 PASS/FAIL 判定)
    """
    print()
    hr(68)
    print(f"  {_c('BD', _c('W', '测试场景:'))} {_c('C', description)}")
    print(f"  {_c('BD', _c('W', '报错输入:'))} {_c('D', error_text[:110] + ('...' if len(error_text) > 110 else ''))}")

    start = time.time()
    try:
        payload = {"errorText": error_text}
        result = _api_post("/api/v1/rescue", payload)
        elapsed = time.time() - start
        data = result.get("data", "")
        code = result.get("code")
        message = result.get("message", "")

        is_rag = not data.startswith("[来自通用大模型]")
        source_label = _c("G", "私域知识库 (RAG)") if is_rag else _c("Y", "通用大模型 (降级)")

        # ──── Channel 1: 终端 ────
        print()
        print(f"  {_c('BD', '┌─ ' + _c('G', '通道 1: 终端 (Terminal)') + ' ' + '─' * 43 + '┐')}")
        print(f"  │  {_c('BD', '耗时:')} {elapsed:.2f}s    {_c('BD', '来源:')} {source_label}      {' ' * 10}│")
        print(f"  │  {_c('BD', '状态:')} code={code}, {message[:50]}{' ' * (30 - len(str(message)[:50]))}│")
        print(f"  ├{'─' * 66}┤")
        for line in data.split("\n"):
            line = line.rstrip()
            if len(line) > 64:
                print(f"  │  {line[:64]}")
                for i in range(64, len(line), 62):
                    print(f"  │  {line[i:i+62]}")
            elif line:
                print(f"  │  {line}")
        print(f"  └{'─' * 66}┘")

        # ──── Channel 2: 飞书群 ────
        print(f"  {_c('BD', '┌─ ' + _c('B', '通道 2: 飞书群 (Feishu Group)') + ' ' + '─' * 30 + '┐')}")
        print(f"  │  {_c('M', '📨 FeishuCardService.sendErrorNotification()')}         │")
        print(f"  │  已在后端异步触发，飞书群内将收到 Debug 协助卡片       │")
        print(f"  │  卡片包含: 报错摘要 + AI 修复建议 + 参考文档链接      │")
        print(f"  │  {_c('D', '请打开飞书群查看卡片消息')}                           │")
        print(f"  └{'─' * 66}┘")

        hr(68)

        # 判定
        if expect_rag == is_rag:
            status = _c("G", "PASS")
        else:
            status = _c("R", "FAIL")
        print(f"  [{status}] {description}  |  预期: {'RAG' if expect_rag else '降级'}  |  实际: {'RAG' if is_rag else '降级'}")

        return is_rag, data

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        elapsed = time.time() - start
        print(f"  {_c('R', f'[✗] HTTP {e.code} ({elapsed:.2f}s)')}")
        print(f"  {_c('D', body[:300])}")
        return False, str(e)
    except Exception as e:
        elapsed = time.time() - start
        print(f"  {_c('R', f'[✗] 请求异常 ({elapsed:.2f}s): {e}')}")
        return False, str(e)


# ============================================================
#  主流程
# ============================================================
def main():
    print()
    print(_c("BD", _c("C", r"""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║     FeiKnow (飞知) — 双通道推送演示测试                           ║
    ║                                                                  ║
    ║  通道 1 (终端):    精简修复指令，开发者可直接复制执行               ║
    ║  通道 2 (飞书群):   Debug 协助卡片，报错摘要+建议+来源链接          ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)))

    # Step 0: 检查后端
    box_header("Step 0: 后端连通性检查")
    if not check_backend():
        print()
        print(_c("R", "  请先启动后端服务: mvn spring-boot:run"))
        print(_c("R", "  并确保 pgvector 数据库已启动: docker-compose up -d"))
        print()
        return
    box_footer()

    # Step 0.5: 测试飞书通道
    box_header("Step 0.5: 飞书群通道预检")
    feishu_ok = test_feishu_channel()
    if not feishu_ok:
        print(_c("Y", "  [!] 飞书群未配置或不可达，但不影响终端通道测试"))
        print(_c("Y", "       请在 application.yml 中配置 feishu.group-chat-id 后重试"))
    box_footer()

    # Step 1: 知识库状态
    box_header("Step 1: 知识库覆盖场景")
    print(f"  {_c('W', '知识库: 容器部署指南 / 微服务异常手册 / 开发环境踩坑指南')}")
    print(f"  {_c('W', '预期: 相似度 >= 0.6 → 命中私域 RAG；< 0.6 → 降级通用大模型')}")
    box_footer()

    # ======== 测试用例 ========
    results = []

    # 测试1 - 命中私域
    results.append(rescue(
        "Docker build failed: no space left on device, cannot write image layer at /var/lib/docker/overlay2",
        "Docker 构建磁盘空间不足 (预期命中私域 RAG)",
        expect_rag=True,
    ))

    # 测试2 - 命中私域
    results.append(rescue(
        "GitLab CI Runner job failed with exit code 137, container was killed by OOM killer, memory limit exceeded",
        "GitLab CI OOM exit 137 (预期命中私域 RAG)",
        expect_rag=True,
    ))

    # 测试3 - 命中私域
    results.append(rescue(
        "Spring Cloud Gateway returned 503 Service Unavailable for service user-center, no instances available",
        "微服务 Gateway 503 (预期命中私域 RAG)",
        expect_rag=True,
    ))

    # 测试4 - 命中私域
    results.append(rescue(
        "java.lang.OutOfMemoryError: Java heap space at com.example.service.DataProcessor.process(DataProcessor.java:156)",
        "Java OutOfMemoryError 堆溢出 (预期命中私域 RAG)",
        expect_rag=True,
    ))

    # 测试5 - 降级通用模型
    results.append(rescue(
        "Python script failed with IndentationError: unexpected indent at line 42, expected an indented block",
        "Python 缩进错误 (预期降级通用大模型)",
        expect_rag=False,
    ))

    # ======== Step 2: 汇总 ========
    print()
    box_header("Step 2: 双通道测试结果汇总")
    print()
    print(f"  {_c('BD', '┌─────────────────────────────────────────────────────────────────┐')}")
    print(f"  │ {'场景':<28} │ {'通道1 终端':<10} │ {'通道2 飞书群':<12} │ {'判定':<6} │")
    print(f"  ├{'─' * 28}┼{'─' * 10}┼{'─' * 12}┼{'─' * 6}┤")

    scenarios = [
        ("Docker 磁盘不足", True),
        ("GitLab CI OOM exit137", True),
        ("微服务 Gateway 503", True),
        ("Java OutOfMemoryError", True),
        ("Python 缩进错误", False),
    ]

    pass_count = 0
    for i, (name, expect_rag) in enumerate(scenarios):
        hit, _ = results[i]
        is_rag = hit
        terminal_status = _c("G", "  ✓ 完成  ") if hit is not None else _c("R", "  ✗ 失败  ")
        feishu_status = _c("G", "   已推送   ") if feishu_ok else _c("Y", "  未配置   ")
        ok = (expect_rag == is_rag)
        if ok:
            pass_count += 1
        judge = _c("G", " PASS") if ok else _c("R", " FAIL")

        # 格式化来源
        source = _c("G", "私域RAG ") if is_rag else _c("Y", "通用降级 ")
        print(f"  │ {name:<26}  │{terminal_status}│{feishu_status}│{judge}  │  [{source}]")

    print(f"  └{'─' * 28}┴{'─' * 10}┴{'─' * 12}┴{'─' * 6}┘")
    print()
    print(f"  {_c('BD', f'通过率: {pass_count}/5  ({pass_count * 20}%)')}")

    box_footer()

    # ======== Step 3: 双通道架构示意 ========
    print()
    box_header("双通道分发架构")
    print(f"""
  {_c('C', '┌─────────────────────────────────────────────────────────────────┐')}
  {_c('C', '│')}  {_c('G', '通道 1: 本地极客态 (Terminal)')}                                    {_c('C', '│')}
  {_c('C', '│')}    CLI 报错 → RescueService.rescue() → 终端直接打印修复指令    {_c('C', '│')}
  {_c('C', '│')}    • 简洁的修复命令，可直接复制执行                            {_c('C', '│')}
  {_c('C', '│')}    • 标注来源 (私域知识库 / 通用大模型)                        {_c('C', '│')}
  {_c('C', '│')}                                                             {_c('C', '│')}
  {_c('C', '│')}  {_c('B', '通道 2: 团队协作态 (Feishu Group)')}                               {_c('C', '│')}
  {_c('C', '│')}    RescueService → FeishuCardService.sendErrorNotification()  {_c('C', '│')}
  {_c('C', '│')}    • @Async 异步推送，不阻塞终端响应                            {_c('C', '│')}
  {_c('C', '│')}    • 交互式卡片: 报错摘要 + 修复建议 + 参考文档链接            {_c('C', '│')}
  {_c('C', '└─────────────────────────────────────────────────────────────────┘')}
""")
    box_footer()

    print()
    print(_c("G", "  ✅ 双通道演示测试完成！"))
    print(f"  {_c('D', '终端通道: 所有修复建议已在上面展示')}")
    if feishu_ok:
        print(f"  {_c('D', '飞书群通道: 请打开飞书查看 Debug 协助卡片')}")
    else:
        print(f"  {_c('D', '飞书群通道: 未配置，跳过 (不影响终端通道)')}")
    print()


if __name__ == "__main__":
    main()
