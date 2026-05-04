package com.feiknow.feiknow.repository;

import com.feiknow.feiknow.entity.KnowledgeChunk;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface KnowledgeChunkRepository extends JpaRepository<KnowledgeChunk, UUID> {

    @Query(value = "SELECT id, content, source_url, embedding, embedding <=> CAST(:embedding AS vector) as distance " +
            "FROM knowledge_chunk " +
            "ORDER BY distance ASC " +
            "LIMIT 3", nativeQuery = true)
    List<Object[]> findTop3Similar(@Param("embedding") float[] embedding);

    @Query(value = "SELECT id, content, source_url, embedding, " +
            "(0.7 * (1 - (embedding <=> CAST(:embedding AS vector))) + " +
            " 0.3 * CASE WHEN content ~* :keywordPattern THEN 1.0 ELSE 0.0 END) as similarity " +
            "FROM knowledge_chunk " +
            "ORDER BY similarity DESC " +
            "LIMIT 3", nativeQuery = true)
    List<Object[]> findTop3Hybrid(@Param("embedding") float[] embedding,
                                  @Param("keywordPattern") String keywordPattern);

}

