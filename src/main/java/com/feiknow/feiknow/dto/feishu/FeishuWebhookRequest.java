package com.feiknow.feiknow.dto.feishu;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
@JsonIgnoreProperties(ignoreUnknown = true)
public class FeishuWebhookRequest {

    private String challenge;

    private String type;

    private String schema;

    private Header header;

    private Event event;

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Header {
        @JsonProperty("event_id")
        private String eventId;
        @JsonProperty("event_type")
        private String eventType;
        @JsonProperty("create_time")
        private String createTime;
    }

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Event {
        private EventObject object;
    }

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class EventObject {
        private Document document;
        private String content;
    }

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Document {
        @JsonProperty("doc_id")
        private String docId;
        private String title;
    }

}
