package com.feiknow.feiknow.service;

import com.feiknow.feiknow.client.AiProviderClient;
import com.feiknow.feiknow.repository.KnowledgeChunkRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class RescueServiceTest {

    @Mock
    private AiProviderClient aiProviderClient;

    @Mock
    private KnowledgeChunkRepository knowledgeChunkRepository;

    @Mock
    private FeishuCardService feishuCardService;

    @InjectMocks
    private RescueService rescueService;

    @Test
    void rescue_WhenSimilarityAboveThreshold_ReturnsKnowledgeBasedAnswer() {
        String errorText = "npm install EACCES permission denied";
        float[] mockEmbedding = new float[1024];
        String mockContent = "npm权限问题解决方案";

        when(aiProviderClient.createEmbedding(errorText)).thenReturn(mockEmbedding);
        when(knowledgeChunkRepository.findTop3Hybrid(eq(mockEmbedding), anyString())).thenReturn(List.<Object[]>of(
                new Object[]{UUID.randomUUID(), mockContent, "https://example.com/docs", new float[1024], 0.7}
        ));
        when(aiProviderClient.createChatCompletion(anyList())).thenReturn("sudo npm install --unsafe-perm");

        String result = rescueService.rescue(errorText);

        assertEquals("sudo npm install --unsafe-perm", result);
        verify(feishuCardService, times(1)).sendErrorNotification(eq(errorText), eq(result), anyList());
    }

    @Test
    void rescue_WhenSimilarityBelowThreshold_ReturnsGeneralAnswerWithTag() {
        String errorText = "unknown error 12345";
        float[] mockEmbedding = new float[1024];

        when(aiProviderClient.createEmbedding(errorText)).thenReturn(mockEmbedding);
        when(knowledgeChunkRepository.findTop3Hybrid(eq(mockEmbedding), anyString())).thenReturn(List.<Object[]>of(
                new Object[]{UUID.randomUUID(), "无关内容", "https://example.com", new float[1024], 0.2}
        ));
        when(aiProviderClient.createChatCompletion(anyList())).thenReturn("建议查看日志详细信息");

        String result = rescueService.rescue(errorText);

        assertTrue(result.startsWith("[来自通用大模型]"));
        assertTrue(result.contains("建议查看日志详细信息"));
        verify(feishuCardService, times(1)).sendErrorNotification(eq(errorText), eq(result), anyList());
    }

    @Test
    void rescue_WhenRateLimited_ReturnsBusyMessage() {
        String errorText = "test error";
        when(aiProviderClient.createEmbedding(errorText)).thenThrow(new RuntimeException("rate limited"));

        String result = rescueService.rescue(errorText);

        assertEquals("系统繁忙，请稍后再试。", result);
        verify(feishuCardService, never()).sendErrorNotification(any(), any(), any());
    }

    @Test
    void rescue_WhenTimeout_ReturnsBusyMessage() {
        String errorText = "test error";
        when(aiProviderClient.createEmbedding(errorText)).thenThrow(new RuntimeException("timeout"));

        String result = rescueService.rescue(errorText);

        assertEquals("系统繁忙，请稍后再试。", result);
        verify(feishuCardService, never()).sendErrorNotification(any(), any(), any());
    }

}
