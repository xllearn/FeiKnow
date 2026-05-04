package com.feiknow.feiknow.client.feishu;

import lombok.Data;
import java.util.List;

@Data
public class FeishuChatResponse {

    private int code;
    private String msg;
    private ChatData data;

    @Data
    public static class ChatData {
        private List<Choice> choices;
    }

    @Data
    public static class Choice {
        private int index;
        private ChatMessage message;
        private String finish_reason;
    }

    @Data
    public static class ChatMessage {
        private String role;
        private String content;
    }

}
