package com.feiknow.feiknow.client.feishu;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FeishuEmbeddingRequest {

    private String model;
    private List<String> input;

}
