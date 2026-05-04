package com.feiknow.feiknow.client.feishu;

import lombok.Data;

@Data
public class FeishuTenantTokenResponse {

    private int code;
    private String msg;
    private String tenant_access_token;
    private int expire;

}
