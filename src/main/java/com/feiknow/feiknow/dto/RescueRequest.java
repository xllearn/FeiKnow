package com.feiknow.feiknow.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class RescueRequest {

    @NotBlank(message = "Error text is required")
    private String errorText;

}
