package com.feiknow.feiknow.service;

import com.feiknow.feiknow.client.AiProviderClient;
import com.feiknow.feiknow.repository.KnowledgeChunkRepository;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

@Service
public class RescueService {

    private static final double SIMILARITY_THRESHOLD = 0.6;

    private static final Set<String> STOP_WORDS = Set.of(
            "the", "is", "at", "in", "of", "to", "a", "an", "and", "or", "for",
            "on", "with", "by", "from", "as", "be", "it", "no", "not", "this",
            "that", "was", "are", "has", "had", "been", "can", "will", "would",
            "could", "should", "may", "do", "does", "did", "but", "if", "so",
            "we", "you", "he", "she", "they", "its", "his", "her", "our", "my"
    );

    private static final String SYSTEM_PROMPT =
            "你是一个命令行故障排查专家。仅根据提供的Context回答用户的问题，给出简短的终端修复指令。如果Context不包含解决方案，请直说不知道。";

    private final AiProviderClient aiProviderClient;
    private final KnowledgeChunkRepository knowledgeChunkRepository;
    private final FeishuCardService feishuCardService;

    public RescueService(AiProviderClient aiProviderClient,
                         KnowledgeChunkRepository knowledgeChunkRepository,
                         FeishuCardService feishuCardService) {
        this.aiProviderClient = aiProviderClient;
        this.knowledgeChunkRepository = knowledgeChunkRepository;
        this.feishuCardService = feishuCardService;
    }

    public String rescue(String errorText) {
        try {
            float[] errorEmbedding = aiProviderClient.createEmbedding(errorText);
            String keywordPattern = extractKeywordPattern(errorText);
            List<Object[]> similarChunks = knowledgeChunkRepository.findTop3Hybrid(errorEmbedding, keywordPattern);

            List<String> contextList = new ArrayList<>();
            List<String> sourceUrls = new ArrayList<>();
            double maxSimilarity = 0;

            for (Object[] chunk : similarChunks) {
                String content = (String) chunk[1];
                String sourceUrl = (String) chunk[2];
                double similarity = ((Number) chunk[4]).doubleValue();
                maxSimilarity = Math.max(maxSimilarity, similarity);
                contextList.add(content);
                if (sourceUrl != null && !sourceUrl.isBlank()) {
                    sourceUrls.add(sourceUrl);
                }
            }

            List<Map<String, String>> messages = new ArrayList<>();
            String result;

            if (maxSimilarity >= SIMILARITY_THRESHOLD) {
                String context = String.join("\n\n", contextList);
                messages.add(Map.of("role", "system", "content", SYSTEM_PROMPT + "\n\nContext:\n" + context));
                messages.add(Map.of("role", "user", "content", "问题：" + errorText));
                result = aiProviderClient.createChatCompletion(messages);
            } else {
                messages.add(Map.of("role", "system", "content", "你是一个命令行故障排查专家。请给出通用的修复建议。"));
                messages.add(Map.of("role", "user", "content", "问题：" + errorText));
                String aiResult = aiProviderClient.createChatCompletion(messages);
                result = "[来自通用大模型]\n" + aiResult;
            }

            feishuCardService.sendErrorNotification(errorText, result, sourceUrls);
            return result;

        } catch (RuntimeException e) {
            if (e.getMessage().contains("rate limited") || e.getMessage().contains("timeout")) {
                return "系统繁忙，请稍后再试。";
            }
            throw e;
        }
    }

    private String extractKeywordPattern(String errorText) {
        String[] tokens = errorText.split("[\\s:;,.()\\[\\]{}<>/\\\\|@#$%^&*+=!?'\"`~]+");
        Set<String> keywords = new LinkedHashSet<>();
        for (String token : tokens) {
            String lower = token.trim().toLowerCase();
            if (lower.length() >= 2 && !STOP_WORDS.contains(lower) && !lower.matches("\\d+")) {
                keywords.add(escapeForPostgresRegex(lower));
            }
        }
        String pattern = keywords.stream().limit(12).collect(Collectors.joining("|"));
        return pattern.isEmpty() ? "xyzzy_no_match_placeholder" : pattern;
    }

    private String escapeForPostgresRegex(String s) {
        StringBuilder sb = new StringBuilder();
        for (char c : s.toCharArray()) {
            if (".*+?^${}()|[]\\".indexOf(c) >= 0) {
                sb.append("\\\\").append(c);
            } else {
                sb.append(c);
            }
        }
        return sb.toString();
    }

}
