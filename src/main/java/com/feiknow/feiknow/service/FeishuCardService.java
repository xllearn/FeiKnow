package com.feiknow.feiknow.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.feiknow.feiknow.client.FeishuApiClient;
import com.feiknow.feiknow.client.feishu.FeishuSendMessageRequest;
import com.feiknow.feiknow.client.feishu.FeishuSendMessageResponse;
import com.feiknow.feiknow.config.FeishuProperties;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
public class FeishuCardService {

    private final FeishuApiClient feishuApiClient;
    private final FeishuProperties feishuProperties;
    private final ObjectMapper objectMapper;

    public FeishuCardService(FeishuApiClient feishuApiClient, FeishuProperties feishuProperties, ObjectMapper objectMapper) {
        this.feishuApiClient = feishuApiClient;
        this.feishuProperties = feishuProperties;
        this.objectMapper = objectMapper;
    }

    @Async
    public void sendErrorNotification(String errorText, String fixSuggestion, List<String> sourceUrls) {
        if (feishuProperties.getGroupChatId() == null || feishuProperties.getGroupChatId().isBlank()) {
            log.warn("Feishu group chat id is not configured, skip sending message");
            return;
        }

        try {
            Map<String, Object> card = buildCardContent(errorText, fixSuggestion, sourceUrls);
            String contentJson = objectMapper.writeValueAsString(card);

            FeishuSendMessageRequest request = new FeishuSendMessageRequest();
            request.setReceive_id(feishuProperties.getGroupChatId());
            request.setMsg_type("interactive");
            request.setContent(contentJson);
            request.setUuid(UUID.randomUUID().toString());

            FeishuSendMessageResponse response = feishuApiClient.sendMessage(request);
            log.info("Feishu notification sent successfully, response: {}", response);

        } catch (Exception e) {
            log.error("Failed to send feishu notification: {}", e.getMessage(), e);
        }
    }

    private Map<String, Object> buildCardContent(String errorText, String fixSuggestion, List<String> sourceUrls) {
        Map<String, Object> card = new HashMap<>();
        card.put("config", Map.of("wide_screen_mode", true));

        List<Map<String, Object>> elements = new ArrayList<>();

        elements.add(Map.of(
                "tag", "markdown",
                "content", "**🚨 FeiKnow 终端异常捕获**\n"
        ));

        elements.add(Map.of(
                "tag", "hr"
        ));

        elements.add(Map.of(
                "tag", "markdown",
                "content", "**📝 报错摘要：**\n```\n" + truncateText(errorText, 300) + "\n```"
        ));

        elements.add(Map.of(
                "tag", "markdown",
                "content", "**💡 修复建议：**\n" + truncateText(fixSuggestion, 500)
        ));

        if (sourceUrls != null && !sourceUrls.isEmpty()) {
            StringBuilder urlContent = new StringBuilder("**📚 参考文档：**\n");
            for (int i = 0; i < Math.min(sourceUrls.size(), 3); i++) {
                urlContent.append("- [文档").append(i + 1).append("](").append(sourceUrls.get(i)).append(")\n");
            }
            elements.add(Map.of(
                    "tag", "markdown",
                    "content", urlContent.toString()
            ));
        }

        card.put("elements", elements);
        return card;
    }

    private String truncateText(String text, int maxLength) {
        if (text == null) return "";
        return text.length() > maxLength ? text.substring(0, maxLength) + "..." : text;
    }

}
