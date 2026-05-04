package com.feiknow.feiknow.client;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Duration;
import java.util.List;
import java.util.Locale;
import java.util.Map;

@Slf4j
@Component
public class AiProviderClient {

    private static final int EMBEDDING_DIMS = 1024;

    private static final List<String> TECH_KEYWORDS = List.of(
            "docker", "container", "kubernetes", "pod", "deployment", "image", "build", "compose",
            "gitlab", "ci", "cd", "pipeline", "runner", "jenkins", "devops",
            "spring", "cloud", "gateway", "microservice", "eureka", "nacos", "feign", "sentinel",
            "seata", "distributed", "transaction", "rocketmq", "message", "queue", "kafka",
            "maven", "gradle", "dependency", "npm", "node", "permission",
            "java", "heap", "memory", "outofmemory", "jvm", "oom",
            "network", "crash", "error", "failed", "timeout", "503", "unavailable",
            "eslint", "git", "hosts", "config", "refresh", "restart",
            "dockerfile", "volume", "disk", "space",
            "log", "debug", "trace", "stack", "exception",
            "hystrix", "circuit", "breaker", "nacos", "consul", "zookeeper",
            "redis", "mysql", "postgresql", "mongodb", "database", "connection",
            "cpu", "thread", "deadlock", "leak", "gc", "garbage",
            "npm", "pip", "yarn", "compile", "link", "undefined", "null",
            "permission", "denied", "access", "forbidden", "unauthorized",
            "linux", "ubuntu", "centos", "windows", "macos", "shell", "bash",
            "ssl", "tls", "certificate", "handshake", "protocol",
            "dns", "resolve", "host", "proxy", "firewall", "port",
            "token", "auth", "oauth", "jwt", "session", "cookie",
            "yaml", "yml", "json", "xml", "properties", "env", "ini",
            "npm", "npx", "webpack", "babel", "eslint", "prettier"
    );

    private final WebClient webClient;
    private final String apiKey;
    private final String chatModel;

    public AiProviderClient(WebClient.Builder webClientBuilder) {
        this.apiKey = System.getenv().getOrDefault("AI_API_KEY",
                System.getProperty("ai.api.key", "your-ai-api-key"));
        String baseUrl = System.getenv().getOrDefault("AI_BASE_URL",
                System.getProperty("ai.base.url", "https://api.deepseek.com"));
        this.chatModel = System.getenv().getOrDefault("AI_CHAT_MODEL",
                System.getProperty("ai.chat.model", "deepseek-chat"));

        this.webClient = webClientBuilder
                .baseUrl(baseUrl)
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + apiKey)
                .build();

        log.info("AiProviderClient initialized: baseUrl={}, model={}", baseUrl, chatModel);
    }

    public float[] createEmbedding(String text) {
        String lower = text.toLowerCase(Locale.ROOT);
        float[] vec = new float[EMBEDDING_DIMS];

        for (int i = 0; i < TECH_KEYWORDS.size() && i < EMBEDDING_DIMS; i++) {
            if (lower.contains(TECH_KEYWORDS.get(i))) {
                vec[i] = 1.0f;
            }
        }

        double norm = 0.0;
        for (float v : vec) {
            norm += (double) v * v;
        }
        if (norm > 0.0) {
            norm = Math.sqrt(norm);
            for (int i = 0; i < vec.length; i++) {
                vec[i] /= norm;
            }
        }

        return vec;
    }

    public String createChatCompletion(List<Map<String, String>> messages) {
        try {
            Map<String, Object> body = Map.of(
                    "model", chatModel,
                    "messages", messages,
                    "temperature", 0.0,
                    "max_tokens", 1024
            );

            Map response = webClient.post()
                    .uri("/v1/chat/completions")
                    .bodyValue(body)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block(Duration.ofSeconds(45));

            if (response == null) {
                throw new RuntimeException("No response from AI chat API");
            }

            List<Map<String, Object>> choices = (List<Map<String, Object>>) response.get("choices");
            if (choices == null || choices.isEmpty()) {
                log.error("AI chat returned no choices: {}", response);
                throw new RuntimeException("AI chat returned no choices");
            }

            Map<String, Object> message = (Map<String, Object>) choices.get(0).get("message");
            return (String) message.get("content");

        } catch (Exception e) {
            log.error("AI chat completion failed: {}", e.getMessage(), e);
            throw new RuntimeException("AI chat completion failed: " + e.getMessage());
        }
    }

}
