package com.feiknow.feiknow.controller;

import com.feiknow.feiknow.client.AiProviderClient;
import com.feiknow.feiknow.common.Result;
import com.feiknow.feiknow.dto.feishu.FeishuWebhookRequest;
import com.feiknow.feiknow.entity.KnowledgeChunk;
import com.feiknow.feiknow.repository.KnowledgeChunkRepository;
import com.feiknow.feiknow.util.TextSplitter;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

@Slf4j
@RestController
@RequestMapping("/api/v1/feishu")
public class FeishuWebhookController {

    private static final ConcurrentHashMap<String, Boolean> PROCESSED_EVENTS = new ConcurrentHashMap<>();
    private static final ReentrantLock LOCK = new ReentrantLock();
    private static final String DOC_URL_PREFIX = "https://feishu.cn/docx/";

    private final ObjectMapper objectMapper;
    private final TextSplitter textSplitter;
    private final KnowledgeChunkRepository knowledgeChunkRepository;
    private final AiProviderClient aiProviderClient;

    public FeishuWebhookController(ObjectMapper objectMapper, TextSplitter textSplitter,
                                   KnowledgeChunkRepository knowledgeChunkRepository,
                                   AiProviderClient aiProviderClient) {
        this.objectMapper = objectMapper;
        this.textSplitter = textSplitter;
        this.knowledgeChunkRepository = knowledgeChunkRepository;
        this.aiProviderClient = aiProviderClient;
    }

    @PostMapping("/webhook")
    public Object webhook(@RequestBody String requestBody) throws JsonProcessingException {
        FeishuWebhookRequest request = objectMapper.readValue(requestBody, FeishuWebhookRequest.class);

        if (request.getChallenge() != null) {
            Map<String, String> response = new HashMap<>();
            response.put("challenge", request.getChallenge());
            return response;
        }

        String eventId = request.getHeader() != null ? request.getHeader().getEventId() : null;
        if (eventId == null || eventId.isEmpty()) {
            return Result.fail(400, "事件ID不能为空");
        }

        LOCK.lock();
        try {
            if (PROCESSED_EVENTS.containsKey(eventId)) {
                return Result.success("事件已处理，无需重复处理", null);
            }
            PROCESSED_EVENTS.put(eventId, true);
        } finally {
            LOCK.unlock();
        }

        String eventType = request.getHeader().getEventType();
        if (!"docx.document.update_v2".equals(eventType)) {
            return Result.success("非文档更新事件，无需处理", null);
        }

        FeishuWebhookRequest.EventObject eventObject = request.getEvent().getObject();
        String content = eventObject.getContent();
        if (content == null || content.trim().isEmpty()) {
            return Result.fail(400, "文档内容不能为空");
        }

        String docId = eventObject.getDocument().getDocId();
        String sourceUrl = DOC_URL_PREFIX + docId;

        List<String> chunks = textSplitter.split(content);

        for (String chunkText : chunks) {
            float[] embedding = aiProviderClient.createEmbedding(chunkText);

            KnowledgeChunk chunk = new KnowledgeChunk();
            chunk.setContent(chunkText);
            chunk.setSourceUrl(sourceUrl);
            chunk.setEmbedding(embedding);
            knowledgeChunkRepository.save(chunk);
        }

        Map<String, Object> data = new HashMap<>();
        data.put("docId", docId);
        data.put("chunkCount", chunks.size());
        data.put("totalLength", content.length());

        return Result.success("处理成功", data);
    }

}
