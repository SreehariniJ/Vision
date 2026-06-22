import logging
from typing import List, Dict, Any, Optional
from neo4j import AsyncGraphDatabase
from app.config import settings

logger = logging.getLogger(__name__)

class GraphStore:
    """Client for Neo4j knowledge graph."""
    
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self._driver = None
        
    async def get_driver(self):
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self._driver
        
    async def close(self):
        if self._driver is not None:
            await self._driver.close()
            self._driver = None
            
    async def insert_document_graph(self, document_id: str, chunk_id: str, chunk_text: str, entities: List[Dict[str, str]], relationships: List[Dict[str, str]]):
        """
        Inserts document chunks, entities, and relationships into Neo4j.
        """
        driver = await self.get_driver()
        
        query = """
        // 1. Create Chunk
        MERGE (c:Chunk {id: $chunk_id})
        SET c.text = $chunk_text, c.document_id = $document_id
        
        // 2. Link Chunk to Document
        MERGE (d:Document {id: $document_id})
        MERGE (c)-[:CONTAINS]->(d)
        
        // 3. Create Entities and Links
        WITH c
        UNWIND $entities AS ent
        MERGE (e:Entity {name: toLower(ent.name)})
        SET e.type = ent.type
        MERGE (c)-[:MENTIONS]->(e)
        
        // 4. Create Relationships
        WITH c
        UNWIND $relationships AS rel
        MERGE (source:Entity {name: toLower(rel.source)})
        MERGE (target:Entity {name: toLower(rel.target)})
        MERGE (source)-[r:RELATED_TO]->(target)
        SET r.description = rel.type
        """
        
        try:
            async with driver.session() as session:
                await session.run(
                    query, 
                    chunk_id=chunk_id, 
                    chunk_text=chunk_text, 
                    document_id=document_id,
                    entities=entities,
                    relationships=relationships
                )
        except Exception as e:
            logger.error(f"Failed to insert graph data: {e}")
            
    async def search_related_entities(self, keywords: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find related entities and the documents/chunks that mention them based on keywords.
        Uses full-text search index created during initialization.
        """
        if not keywords:
            return []
            
        # Join keywords for full-text search: "keyword1 OR keyword2"
        query_str = " OR ".join(f"*{kw}*" for kw in keywords)
        
        query = """
        CALL db.index.fulltext.queryNodes("entity_name_index", $query_str) YIELD node AS entity, score
        MATCH (entity)<-[:MENTIONS]-(chunk:Chunk)-[:CONTAINS]-(doc:Document)
        OPTIONAL MATCH (entity)-[r:RELATED_TO]-(related:Entity)
        RETURN 
            entity.name AS entity_name,
            entity.type AS entity_type,
            collect(DISTINCT related.name) AS related_entities,
            collect(DISTINCT chunk.text) AS chunk_texts,
            collect(DISTINCT doc.title) AS document_titles,
            score
        ORDER BY score DESC
        LIMIT $limit
        """
        
        driver = await self.get_driver()
        try:
            async with driver.session() as session:
                result = await session.run(query, query_str=query_str, limit=limit)
                records = await result.data()
                return records
        except Exception as e:
            logger.error(f"Graph search failed: {e}")
            return []

# Singleton instance
graph_store = GraphStore()
