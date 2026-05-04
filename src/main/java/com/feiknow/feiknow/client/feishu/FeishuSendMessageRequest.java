package com.feiknow.feiknow.client.feishu;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FeishuSendMessageRequest {

    private String receive_id;
    private String msg_type;
    private String content;
    private String uuid;

}
