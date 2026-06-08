// ============================================================
// Vision - Neo4j Initialization Script
// ============================================================

// --- Constraints (Unique IDs) ---
CREATE CONSTRAINT document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:Chunk) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE;
CREATE CONSTRAINT topic_name IF NOT EXISTS FOR (t:Topic) REQUIRE t.name IS UNIQUE;

// --- Indexes ---
CREATE INDEX document_title IF NOT EXISTS FOR (d:Document) ON (d.title);
CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type);

// --- Full-Text Search Indexes ---
// Neo4j 5 syntax for full-text search
CREATE FULLTEXT INDEX chunk_text_index IF NOT EXISTS FOR (n:Chunk) ON EACH [n.text];
CREATE FULLTEXT INDEX entity_name_index IF NOT EXISTS FOR (n:Entity) ON EACH [n.name];

// Note: Relationships to be created dynamically during ingestion:
// (Document)-[:CONTAINS]->(Chunk)
// (Chunk)-[:MENTIONS]->(Entity)
// (Document)-[:ABOUT]->(Topic)
// (Entity)-[:RELATED_TO {type: '...', confidence: 0.9}]->(Entity)
