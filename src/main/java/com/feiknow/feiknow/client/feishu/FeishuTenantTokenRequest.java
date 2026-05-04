package com.feiknow.feiknow.client.feishu;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FeishuTenantTokenRequest {

    private String app_id;
    private String app_secret;

}
