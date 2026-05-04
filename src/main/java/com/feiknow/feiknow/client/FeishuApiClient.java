package com.feiknow.feiknow.client;

import com.feiknow.feiknow.client.feishu.*;
import com.feiknow.feiknow.config.FeishuProperties;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import java.time.Duration;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;

@Slf4j
@Component
public class FeishuApiClient {

    private final WebClient webClient;
    private final FeishuProperties properties;
    private final AtomicReference<String> cachedToken = new AtomicReference<>();
    private volatile long tokenExpireTime = 0;

    public FeishuApiClient(FeishuProperties properties, WebClient.Builder webClientBuilder) {
        this.properties = properties;
        this.webClient = webClientBuilder
                .baseUrl(properties.getBaseUrl())
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .build();
    }

    public String getTenantAccessToken() {
        long now = System.currentTimeMillis() / 1000;
        if (cachedToken.get() != null && now < tokenExpireTime - 60) {
            return cachedToken.get();
        }

        synchronized (this) {
            if (cachedToken.get() != null && now < tokenExpireTime - 60) {
                return cachedToken.get();
            }

            FeishuTenantTokenRequest request = new FeishuTenantTokenRequest(
                    properties.getAppId(),
                    properties.getAppSecret()
            );

            FeishuTenantTokenResponse response = webClient.post()
                    .uri("/open-apis/auth/v3/tenant_access_token/internal")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(FeishuTenantTokenResponse.class)
                    .block(Duration.ofSeconds(5));

            if (response == null || response.getCode() != 0) {
                log.error("Failed to get feishu tenant access token, code: {}, msg: {}",
                        response != null ? response.getCode() : -1,
                        response != null ? response.getMsg() : "response is null");
                throw new RuntimeException("Failed to get feishu access token");
            }

            cachedToken.set(response.getTenant_access_token());
            tokenExpireTime = now + response.getExpire();
            log.info("Feishu tenant access token refreshed, expires in {} seconds", response.getExpire());
            return cachedToken.get();
        }
    }

    public FeishuSendMessageResponse sendMessage(FeishuSendMessageRequest request) {
        String token = getTenantAccessToken();

        try {
            FeishuSendMessageResponse response = webClient.post()
                    .uri("/open-apis/im/v1/messages?receive_id_type=chat_id")
                    .header(HttpHeaders.AUTHORIZATION, "Bearer " + token)
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(FeishuSendMessageResponse.class)
                    .block(Duration.ofSeconds(5));

            if (response == null || response.getCode() != 0) {
                log.error("Failed to send feishu message, code: {}, msg: {}, request: {}",
                        response != null ? response.getCode() : -1,
                        response != null ? response.getMsg() : "response is null",
                        request);
                throw new RuntimeException("Failed to send feishu message: " + (response != null ? response.getMsg() : "no response"));
            }

            log.info("Feishu message sent successfully, response: {}", response);
            return response;
        } catch (WebClientResponseException e) {
            log.error("Feishu sendMessage HTTP error, status: {}, body: {}, request: {}",
                    e.getStatusCode(), e.getResponseBodyAsString(), request);
            throw new RuntimeException("Feishu sendMessage failed: " + e.getStatusCode() + " - " + e.getResponseBodyAsString());
        }
    }

    public float[] createEmbedding(String text) {
        String token = getTenantAccessToken();
        FeishuEmbeddingRequest request = new FeishuEmbeddingRequest(
                "embedding-001",
                List.of(text)
        );

        FeishuEmbeddingResponse response = webClient.post()
                .uri("/open-apis/ai/v1/embeddings")
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + token)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(FeishuEmbeddingResponse.class)
                .block(Duration.ofSeconds(10));

        if (response == null || response.getCode() != 0) {
            log.error("Failed to get embedding from feishu, code: {}, msg: {}",
                    response != null ? response.getCode() : -1,
                    response != null ? response.getMsg() : "response is null");
            throw new RuntimeException("Failed to get embedding");
        }

        return response.getData().getEmbeddings().get(0).getEmbedding();
    }

    public String createChatCompletion(List<FeishuChatRequest.ChatMessage> messages) {
        String token = getTenantAccessToken();
        FeishuChatRequest request = new FeishuChatRequest(
                "gpt-3.5-turbo",
                messages,
                0.0
        );

        FeishuChatResponse response = webClient.post()
                .uri("/open-apis/ai/v1/chat/completions")
                .header(HttpHeaders.AUTHORIZATION, "Bearer " + token)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(FeishuChatResponse.class)
                .block(Duration.ofSeconds(30));

        if (response == null || response.getCode() != 0) {
            log.error("Failed to get chat completion from feishu, code: {}, msg: {}",
                    response != null ? response.getCode() : -1,
                    response != null ? response.getMsg() : "response is null");
            throw new RuntimeException("Failed to get chat completion");
        }

        return response.getData().getChoices().get(0).getMessage().getContent();
    }

}
