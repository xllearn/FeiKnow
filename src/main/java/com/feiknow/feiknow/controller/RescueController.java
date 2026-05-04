package com.feiknow.feiknow.controller;

import com.feiknow.feiknow.common.Result;
import com.feiknow.feiknow.dto.RescueRequest;
import com.feiknow.feiknow.service.FeishuCardService;
import com.feiknow.feiknow.service.RescueService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/v1/rescue")
public class RescueController {

    private final RescueService rescueService;
    private final FeishuCardService feishuCardService;

    public RescueController(RescueService rescueService, FeishuCardService feishuCardService) {
        this.rescueService = rescueService;
        this.feishuCardService = feishuCardService;
    }

    @PostMapping
    public Result<String> rescue(@Valid @RequestBody RescueRequest request) {
        String result = rescueService.rescue(request.getErrorText());
        return Result.success(result);
    }
    
    @GetMapping("/test-feishu")
    public Result<String> testFeishu() {
        feishuCardService.sendErrorNotification("test error", "Hello FeiKnow, 这是一个 Test 测试卡片", List.of("https://github.com/feiknow"));
        return Result.success("测试消息已发送，请检查飞书群");
    }

}
