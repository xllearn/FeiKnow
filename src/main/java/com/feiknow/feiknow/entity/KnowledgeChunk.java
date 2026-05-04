package com.feiknow.feiknow.entity;

import jakarta.persistence.*;
import lombok.Data;

import java.util.UUID;

@Data
@Entity
@Table(name = "knowledge_chunk")
public class KnowledgeChunk {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;

    @Column(name = "source_url")
    private String sourceUrl;

    @Column(columnDefinition = "vector(1024)", nullable = false)
    private float[] embedding;

}
