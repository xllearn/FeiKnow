package com.feiknow.feiknow.client.feishu;

import lombok.Data;
import java.util.List;

@Data
public class FeishuEmbeddingResponse {

    private int code;
    private String msg;
    private EmbeddingData data;

    @Data
    public static class EmbeddingData {
        private List<Embedding> embeddings;
    }

    @Data
    public static class Embedding {
        private float[] embedding;
        private int index;
    }

}
