package com.feiknow.feiknow.client.feishu;

import lombok.Data;

@Data
public class FeishuSendMessageResponse {

    private int code;
    private String msg;
    private Object data;

}
