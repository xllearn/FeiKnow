package com.feiknow.feiknow.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class PingRequest {

    @NotBlank(message = "内容不能为空")
    private String content;

    private String sourceUrl;

}
