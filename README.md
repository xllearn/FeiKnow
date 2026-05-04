# FeiKnow（飞知）

<p align="center">
  <b>极客专属的终端知识调度引擎 —— 让知识主动找到你</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Java-17-blue" alt="Java 17">
  <img src="https://img.shields.io/badge/Spring%20Boot-3.3-brightgreen" alt="Spring Boot 3.3">
  <img src="https://img.shields.io/badge/PostgreSQL-pgvector-orange" alt="PostgreSQL pgvector">
  <img src="https://img.shields.io/badge/Python-3-blue" alt="Python 3">
</p>

---

## 一、项目简介

FeiKnow（飞知）是一款面向研发团队的「主动式」CLI 终端知识调度引擎，联动飞书生态，实现知识获取范式从 **"人找知识"** 到 **"知识找人"** 的跃迁。

当开发者在终端执行命令失败时，FeiKnow 自动捕获报错信息，通过 **RAG（检索增强生成）** 技术在私域知识库中检索相关解决方案，并在**终端**和**飞书群**两个通道同步推送修复建议。

```
传统方式：复制报错 → 切浏览器 → 搜 Wiki → 翻文档 → 找方案（3-5 分钟）
FeiKnow： 命令失败 → 自动捕获 → RAG 检索 → AI 生成 → 终端+飞书推送（< 30 秒）
```

## 二、核心特性

| 特性 | 说明 |
|------|------|
| 🔍 **混合检索** | `0.7 × 向量余弦相似度 + 0.3 × 关键词命中`，一条 SQL 完成排序 |
| 🧠 **RAG 增强生成** | 私域 Context 注入 System Prompt，杜绝 AI 幻觉 |
| 📡 **双通道推送** | 终端打印精简修复指令 + 飞书群推送 Debug 协助卡片 |
| 🔽 **智能降级** | 知识库匹配不足时自动切换通用大模型，并显式标注来源 |
| ⚡ **事件驱动** | 飞书文档更新 → Webhook → 自动分块 → 向量化入库 |
| 🔑 **Token 缓存** | 双重检查锁 + 过期前 60s 提前刷新 |
| 🏗️ **关键词向量引擎** | 100+ 技术关键词映射为 1024 维特征向量，无需外部 Embedding API |
| 🐳 **一键部署** | `docker-compose up -d` 启动 pgvector + `mvn spring-boot:run` 启动服务 |

## 三、技术架构

```
┌──────────────┐     HTTP/REST      ┌──────────────────────────┐      HTTPS       ┌─────────────────┐
│  CLI 客户端   │ ─────────────────→ │     Spring Boot 后端      │ ←─────────────→ │  DeepSeek API    │
│  (Python 3)  │                    │     (Java 17 / Boot 3)   │                  │  Chat Completion │
└──────────────┘                    │                          │                  └─────────────────┘
                                    │  ┌────────────────────┐  │
 ┌──────────────┐   Webhook JSON   │  │ RescueService       │  │     HTTPS        ┌─────────────────┐
 │ 飞书文档更新  │ ───────────────→ │  │  (RAG 核心引擎)     │  │ ←─────────────→ │  飞书 IM API     │
 └──────────────┘                   │  └─────────┬──────────┘  │                  │  卡片消息推送     │
                                    │            │              │                  └─────────────────┘
                                    │  ┌─────────▼──────────┐  │
                                    │  │ pgvector 向量库     │  │
                                    │  │ (PostgreSQL 16)    │  │
                                    │  │ 1024-dim vectors   │  │
                                    │  └────────────────────┘  │
                                    └──────────────────────────┘
```

### 核心流程

```
📥 知识吸收 → ⚡ 事件触发 → 🧠 混合检索+RAG → 📤 双通道分发

飞书文档更新         命令失败            pgvector 混合排序      终端打印修复指令
Webhook 触发         CLI 自动捕获        Top-3 知识片段         飞书推送 Debug 卡片
自动分块+向量化入库   POST /api/rescue   相似度≥0.6 → RAG       含报错摘要+建议+来源
```

## 四、快速开始

### 环境要求

- **JDK** 17+
- **Maven** 3.8+
- **Python** 3.x（CLI 客户端）
- **Docker**（推荐）

### 1. 克隆项目

```bash
git clone https://github.com/xllearn/FeiKnow.git
cd FeiKnow
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的真实配置
```

必须配置的环境变量：

| 变量 | 说明 |
|------|------|
| `FEISHU_APP_ID` | 飞书应用 App ID |
| `FEISHU_APP_SECRET` | 飞书应用 App Secret |
| `AI_API_KEY` | DeepSeek API Key |

### 3. 启动 PostgreSQL + pgvector

```bash
docker-compose up -d
```

### 4. 启动后端服务

```bash
mvn spring-boot:run -Dspring-boot.run.profiles=dev
```

### 5. 安装 CLI 客户端

```bash
# 将 client/feiknow.py 添加到 PATH
# 或创建别名
alias feiknow='python3 /path/to/client/feiknow.py'
```

### 6. 使用

```bash
# 用 feiknow 替代你的命令，失败时自动分析
feiknow docker build .
feiknow mvn compile
feiknow npm install
```

## 五、项目结构

```
FeiKnow/
├── client/
│   └── feiknow.py                  # Python CLI 终端代理（命令包装器）
├── src/main/java/com/feiknow/feiknow/
│   ├── FeiKnowApplication.java     # Spring Boot 入口
│   ├── client/
│   │   ├── AiProviderClient.java   # AI 调用 + 关键词向量引擎
│   │   ├── FeishuApiClient.java    # 飞书认证 / IM API 封装
│   │   └── feishu/                 # 飞书 API 请求/响应 DTO
│   ├── config/
│   │   ├── AsyncConfig.java        # 异步线程池配置
│   │   └── FeishuProperties.java   # 飞书配置属性绑定
│   ├── controller/
│   │   ├── FeishuWebhookController.java  # 飞书文档更新 Webhook
│   │   ├── RescueController.java         # CLI 救援请求入口
│   │   └── PingController.java           # 健康检查
│   ├── service/
│   │   ├── RescueService.java      # RAG 核心引擎（混合检索）
│   │   └── FeishuCardService.java  # 飞书卡片消息推送
│   ├── repository/
│   │   └── KnowledgeChunkRepository.java # pgvector 混合检索 SQL
│   ├── entity/
│   │   └── KnowledgeChunk.java     # 知识分块实体（1024 维向量）
│   ├── util/
│   │   └── TextSplitter.java       # 滑动窗口文本分块
│   └── ...
├── src/main/resources/
│   ├── application.yml             # 生产配置（环境变量注入）
│   └── application-dev.yml         # 开发配置
├── src/test/                       # 单元测试 + 集成测试（TestContainers）
├── docker-compose.yml              # pgvector 一键启动
├── init.sql                        # 数据库初始化
├── mock_feishu_server.py           # 飞书 Mock 服务器（本地开发用）
├── .env.example                    # 环境变量模板
├── test_*.py                       # API 测试脚本
└── 场景定义文档.md                   # 项目规划设计文档
```

## 六、API 接口

### POST /api/v1/rescue

CLI 救援请求，分析报错并返回修复建议。

**请求体：**

```json
{
  "errorText": "Docker build failed: no space left on device"
}
```

**响应：**

```json
{
  "code": 200,
  "message": "处理成功",
  "data": "执行 docker system prune -a 清理未使用的镜像和容器，然后 df -h 检查磁盘空间。"
}
```

### POST /api/v1/ping

健康检查与知识入库测试。

### POST /api/v1/feishu/webhook

飞书文档更新 Webhook 接收端点，自动触发知识分块与向量化入库。

## 七、技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | Spring Boot 3.3 | Java 17 |
| 向量数据库 | PostgreSQL 16 + pgvector 0.7 | 1024 维向量存储与余弦距离检索 |
| ORM | Spring Data JPA | 原生 SQL 混合检索 |
| HTTP 框架 | WebClient (WebFlux) | 非阻塞 IO |
| 大语言模型 | DeepSeek Chat API | RAG 增强生成 |
| 消息推送 | 飞书 IM API | 交互式卡片消息 |
| CLI 客户端 | Python 3 | 跨平台命令代理 |
| 测试框架 | JUnit 5 + TestContainers | 集成测试 |
| 容器化 | Docker Compose | pgvector 快速部署 |

## 八、本地开发

### 启动 Mock 飞书服务器

```bash
# 终端 1：启动 Mock 服务（无需真实飞书凭据）
python mock_feishu_server.py
```

Mock 服务器会在 `localhost:18080` 模拟飞书 Token、Embedding 和 Chat 接口，方便本地开发调试。

### 测试知识入库

```bash
python test_webhook.py        # 模拟飞书文档 Webhook 推送
```

### 测试 RAG 检索

```bash
python test_rescue.py          # 端到端测试 RAG 检索和降级策略
python test_dual_channel.py    # 终端 + 飞书 双通道推送测试
```

## 九、许可证

MIT License

---

<p align="center">
  <b>FeiKnow — 让每一次报错都成为团队的知识资产</b>
</p>
