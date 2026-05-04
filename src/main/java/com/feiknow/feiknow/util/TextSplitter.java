package com.feiknow.feiknow.util;

import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

@Component
public class TextSplitter {

    private static final int CHUNK_SIZE = 500;
    private static final int OVERLAP_SIZE = 50;

    public List<String> split(String text) {
        List<String> chunks = new ArrayList<>();
        if (text == null || text.isEmpty()) {
            return chunks;
        }

        int length = text.length();
        if (length <= CHUNK_SIZE) {
            chunks.add(text);
            return chunks;
        }

        int start = 0;
        while (start < length) {
            int end = Math.min(start + CHUNK_SIZE, length);
            String chunk = text.substring(start, end);
            chunks.add(chunk);
            start += CHUNK_SIZE - OVERLAP_SIZE;

            if (end == length) {
                break;
            }
        }

        return chunks;
    }

}
