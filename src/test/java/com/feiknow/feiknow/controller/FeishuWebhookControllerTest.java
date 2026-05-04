package com.feiknow.feiknow.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class FeishuWebhookControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void shouldReturnChallengeWhenRequestContainsChallengeField() throws Exception {
        String requestBody = "{\"challenge\":\"test-challenge-123\",\"type\":\"url_verification\"}";

        mockMvc.perform(post("/api/v1/feishu/webhook")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(content().string("{\"challenge\":\"test-challenge-123\"}"));
    }

    @Test
    void shouldReturnBadRequestWhenJsonFormatIsInvalid() throws Exception {
        String invalidJson = "{\"invalid\": \"json\", missing bracket";

        mockMvc.perform(post("/api/v1/feishu/webhook")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(invalidJson))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(400))
                .andExpect(jsonPath("$.message").exists());
    }

    @Test
    void shouldReturnSuccessWhenReceiveDocumentUpdateEvent() throws Exception {
        String requestBody = "{\n" +
                "  \"schema\": \"2.0\",\n" +
                "  \"header\": {\n" +
                "    \"event_id\": \"event-12345\",\n" +
                "    \"event_type\": \"docx.document.update_v2\",\n" +
                "    \"create_time\": \"1680000000000\"\n" +
                "  },\n" +
                "  \"event\": {\n" +
                "    \"object\": {\n" +
                "      \"document\": {\n" +
                "        \"doc_id\": \"doc-abc123\",\n" +
                "        \"title\": \"测试文档\"\n" +
                "      },\n" +
                "      \"content\": \"这是一段测试文档内容，长度小于500字符。\"\n" +
                "    }\n" +
                "  }\n" +
                "}";

        mockMvc.perform(post("/api/v1/feishu/webhook")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("处理成功"));
    }

    @Test
    void shouldHandleLongTextSplittingCorrectly() throws Exception {
        StringBuilder longText = new StringBuilder();
        for (int i = 0; i < 2000; i++) {
            longText.append("测试文本");
        }

        String requestBody = "{\n" +
                "  \"schema\": \"2.0\",\n" +
                "  \"header\": {\n" +
                "    \"event_id\": \"event-67890\",\n" +
                "    \"event_type\": \"docx.document.update_v2\",\n" +
                "    \"create_time\": \"1680000000000\"\n" +
                "  },\n" +
                "  \"event\": {\n" +
                "    \"object\": {\n" +
                "      \"document\": {\n" +
                "        \"doc_id\": \"doc-xyz789\",\n" +
                "        \"title\": \"长文档测试\"\n" +
                "      },\n" +
                "      \"content\": \"" + longText + "\"\n" +
                "    }\n" +
                "  }\n" +
                "}";

        mockMvc.perform(post("/api/v1/feishu/webhook")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.chunkCount").exists());
    }

    @Test
    void shouldReturnBadRequestWhenDocumentContentIsEmpty() throws Exception {
        String requestBody = "{\n" +
                "  \"schema\": \"2.0\",\n" +
                "  \"header\": {\n" +
                "    \"event_id\": \"event-empty-123\",\n" +
                "    \"event_type\": \"docx.document.update_v2\",\n" +
                "    \"create_time\": \"1680000000000\"\n" +
                "  },\n" +
                "  \"event\": {\n" +
                "    \"object\": {\n" +
                "      \"document\": {\n" +
                "        \"doc_id\": \"doc-empty-123\",\n" +
                "        \"title\": \"空文档测试\"\n" +
                "      },\n" +
                "      \"content\": \"\"\n" +
                "    }\n" +
                "  }\n" +
                "}";

        mockMvc.perform(post("/api/v1/feishu/webhook")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value(400))
                .andExpect(jsonPath("$.message").value("文档内容不能为空"));
    }

    @Test
    void shouldReturnSuccessWhenReceiveDuplicateEvent() throws Exception {
        String requestBody = "{\n" +
                "  \"schema\": \"2.0\",\n" +
                "  \"header\": {\n" +
                "    \"event_id\": \"event-duplicate-123\",\n" +
                "    \"event_type\": \"docx.document.update_v2\",\n" +
                "    \"create_time\": \"1680000000000\"\n" +
                "  },\n" +
                "  \"event\": {\n" +
                "    \"object\": {\n" +
                "      \"document\": {\n" +
                "        \"doc_id\": \"doc-duplicate-123\",\n" +
                "        \"title\": \"重复事件测试\"\n" +
                "      },\n" +
                "      \"content\": \"重复事件测试内容\"\n" +
                "    }\n" +
                "  }\n" +
                "}";

        mockMvc.perform(post("/api/v1/feishu/webhook")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));

        mockMvc.perform(post("/api/v1/feishu/webhook")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.message").value("事件已处理，无需重复处理"));
    }

}
