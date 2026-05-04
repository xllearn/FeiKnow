package com.feiknow.feiknow.controller;

import com.feiknow.feiknow.common.Result;
import com.feiknow.feiknow.dto.PingRequest;
import com.feiknow.feiknow.entity.KnowledgeChunk;
import com.feiknow.feiknow.repository.KnowledgeChunkRepository;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

@RestController
@RequestMapping("/api/v1")
public class PingController {

    private final KnowledgeChunkRepository knowledgeChunkRepository;
    private final Random random = new Random();

    public PingController(KnowledgeChunkRepository knowledgeChunkRepository) {
        this.knowledgeChunkRepository = knowledgeChunkRepository;
    }

    @PostMapping("/ping")
    public Result<Map<String, Object>> ping(@Valid @RequestBody PingRequest request) {
        float[] embedding = new float[1024];
        for (int i = 0; i < 1024; i++) {
            embedding[i] = random.nextFloat();
        }

        KnowledgeChunk chunk = new KnowledgeChunk();
        chunk.setContent(request.getContent());
        chunk.setSourceUrl(request.getSourceUrl());
        chunk.setEmbedding(embedding);

        KnowledgeChunk savedChunk = knowledgeChunkRepository.save(chunk);

        Map<String, Object> data = new HashMap<>();
        data.put("id", savedChunk.getId());
        data.put("content", savedChunk.getContent());
        data.put("sourceUrl", savedChunk.getSourceUrl());

        return Result.success("保存成功", data);
    }

}
