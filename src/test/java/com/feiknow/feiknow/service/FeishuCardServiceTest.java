package com.feiknow.feiknow.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.feiknow.feiknow.client.FeishuApiClient;
import com.feiknow.feiknow.client.feishu.FeishuSendMessageRequest;
import com.feiknow.feiknow.config.FeishuProperties;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class FeishuCardServiceTest {

    @Mock
    private FeishuApiClient feishuApiClient;

    @Mock
    private FeishuProperties feishuProperties;

    @Mock
    private ObjectMapper objectMapper;

    @InjectMocks
    private FeishuCardService feishuCardService;

    @Test
    void sendErrorNotification_WhenGroupIdNotConfigured_DoNothing() {
        when(feishuProperties.getGroupChatId()).thenReturn("");

        feishuCardService.sendErrorNotification("test error", "test fix", List.of());

        verify(feishuApiClient, never()).sendMessage(any());
    }

    @Test
    void sendErrorNotification_WithValidData_SendCorrectMessage() throws Exception {
        when(feishuProperties.getGroupChatId()).thenReturn("test-group-id");
        when(objectMapper.writeValueAsString(any())).thenReturn("{\"type\":\"template\"}");

        String errorText = "npm install EACCES permission denied";
        String fixSuggestion = "sudo npm install --unsafe-perm";
        List<String> sourceUrls = List.of("https://docs.example.com/npm-permission", "https://docs.example.com/npm-guide");

        feishuCardService.sendErrorNotification(errorText, fixSuggestion, sourceUrls);

        ArgumentCaptor<FeishuSendMessageRequest> requestCaptor = ArgumentCaptor.forClass(FeishuSendMessageRequest.class);
        verify(feishuApiClient, times(1)).sendMessage(requestCaptor.capture());

        FeishuSendMessageRequest request = requestCaptor.getValue();
        assertEquals("test-group-id", request.getReceive_id());
        assertEquals("interactive", request.getMsg_type());

        String content = request.getContent();
        assertNotNull(content);
        assertTrue(content.contains("template"));
    }

    @Test
    void sendErrorNotification_WhenApiThrowsException_HandleGracefully() {
        when(feishuProperties.getGroupChatId()).thenReturn("test-group-id");
        when(feishuApiClient.sendMessage(any())).thenThrow(new RuntimeException("API error"));

        assertDoesNotThrow(() -> {
            feishuCardService.sendErrorNotification("test error", "test fix", List.of());
        });
    }

}
