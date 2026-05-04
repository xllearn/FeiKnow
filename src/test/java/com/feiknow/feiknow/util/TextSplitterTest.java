package com.feiknow.feiknow.util;

import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class TextSplitterTest {

    private final TextSplitter textSplitter = new TextSplitter();

    @Test
    void shouldReturnEmptyListWhenTextIsNull() {
        List<String> chunks = textSplitter.split(null);
        assertTrue(chunks.isEmpty());
    }

    @Test
    void shouldReturnEmptyListWhenTextIsEmpty() {
        List<String> chunks = textSplitter.split("");
        assertTrue(chunks.isEmpty());
    }

    @Test
    void shouldReturnSingleChunkWhenTextLengthLessThanChunkSize() {
        String text = "这是一段长度只有30字符的短文本，不需要分块。";
        List<String> chunks = textSplitter.split(text);
        assertEquals(1, chunks.size());
        assertEquals(text, chunks.get(0));
    }

    @Test
    void shouldSplitTextCorrectlyWithOverlap() {
        // 生成600字符的文本
        StringBuilder text = new StringBuilder();
        for (int i = 0; i < 600; i++) {
            text.append("测");
        }
        String fullText = text.toString();

        List<String> chunks = textSplitter.split(fullText);
        assertEquals(2, chunks.size());
        assertEquals(500, chunks.get(0).length());
        // 第二个块是后100 + 50重叠 = 150？不对：总长度600，第一个块0-500，第二个块从450开始，450-600=150字符
        assertEquals(150, chunks.get(1).length());
        // 验证重叠部分正确
        assertEquals(fullText.substring(450, 500), chunks.get(1).substring(0, 50));
    }

    @Test
    void shouldSplitLongTextCorrectly() {
        // 生成2000字符的文本
        StringBuilder text = new StringBuilder();
        for (int i = 0; i < 2000; i++) {
            text.append("试");
        }

        List<String> chunks = textSplitter.split(text.toString());
        // 计算预期块数：(2000 - 50) / (500-50) = 1950/450 ≈ 4.33 → 5块
        assertEquals(5, chunks.size());
    }

}
