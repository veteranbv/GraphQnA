"""Knowledge graph retrieval for direct graph queries."""

import logging
import time
from typing import Any, Dict, List, Optional, Union

from neo4j_graphrag.generation import GraphRAG, RagTemplate
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.retrievers import Text2CypherRetriever

from graphqna.config import Settings, get_settings
from graphqna.db import Neo4jDatabase
from graphqna.models.entity import Entity, Relationship
from graphqna.models.response import KnowledgeGraphQueryResult, QueryResponse
from graphqna.retrieval.base import BaseRetriever

logger = logging.getLogger(__name__)


class KnowledgeGraphRetriever(BaseRetriever):
    """
    Knowledge graph retriever for direct Cypher queries.
    
    This retriever uses the LLM to generate Cypher queries to directly
    query the knowledge graph for answers.
    """

    def __init__(
        self,
        db: Optional[Neo4jDatabase] = None,
        settings: Optional[Settings] = None,
        **kwargs
    ):
        """
        Initialize the knowledge graph retriever.
        
        Args:
            db: Neo4j database connection (optional)
            settings: Application settings (optional)
            **kwargs: Additional keyword arguments passed to the parent class
        """
        super().__init__(db=db, settings=settings, **kwargs)
        
        # Create the LLM for answering questions
        self.llm = OpenAILLM(
            model_name=self.settings.llm.model,
            api_key=self.settings.llm.api_key,
            model_params={
                "temperature": self.settings.llm.temperature,
            }
        )
        
        # Generate schema description
        neo4j_schema = self._get_kg_schema()
        
        # Initialize the Text2Cypher retriever
        self.kg_retriever = Text2CypherRetriever(
            driver=self.db.get_driver(),
            llm=self.llm,
            neo4j_schema=neo4j_schema,
        )
        
        # Create the prompt template for kg retrieval
        self.prompt_template = RagTemplate(
            template="""
            Answer the following question based on the information retrieved directly from the knowledge graph:
            
            Question: {query_text}
            
            Context: {context}
            
            Guidelines:
            1. Use ONLY information that is EXPLICITLY returned from the knowledge graph query.
            2. Do not augment the knowledge graph results with general knowledge.
            3. If the knowledge graph contains incomplete information, provide only what can be directly verified.
            4. If no relevant information is returned, respond with "{not_applicable}"
            5. Be precise about entities and relationships in your answer, citing the specific data returned.
            6. End with: "{verify_info}"
            """,
            expected_inputs=["context", "query_text"]
        )
        
    def _get_kg_schema(self) -> str:
        """
        Generate a schema description for the knowledge graph based on database inspection.
        
        Returns:
            str: Schema for the Text2Cypher retriever
        """
        try:
            # Get node labels and their properties from the database
            node_labels_query = """
            CALL db.schema.nodeTypeProperties() 
            YIELD nodeType, propertyName
            RETURN nodeType, collect(propertyName) as properties
            """
            
            # Get relationship types from the database
            rel_types_query = """
            CALL db.schema.relationshipTypeProperties()
            YIELD relType, sourceNodeType, targetNodeType, propertyName
            RETURN 
                sourceNodeType, 
                relType, 
                targetNodeType, 
                collect(propertyName) as properties
            """
            
            with self.db.session() as session:
                # Get node labels and properties
                try:
                    node_types = session.run(node_labels_query).data()
                except Exception:
                    # Fall back to a simpler approach for older Neo4j versions
                    node_types = self._get_node_types_fallback(session)
                    
                # Get relationship types
                try:
                    rel_types = session.run(rel_types_query).data()
                except Exception:
                    # Fall back to a simpler approach for older Neo4j versions
                    rel_types = self._get_rel_types_fallback(session)
            
            # Build the schema string
            schema = "Node properties:\n"
            
            # Add node properties
            for node in node_types:
                node_type = node.get("nodeType", "").replace(":`", "").replace("`", "")
                # Skip internal node types
                if node_type.startswith("__") or not node_type:
                    continue
                    
                properties = node.get("properties", [])
                # Format properties with type
                prop_list = []
                for prop in properties:
                    if prop not in ["embedding", "text"] and not prop.startswith("__"):
                        prop_list.append(f"{prop}: STRING")
                        
                if prop_list:
                    schema += f"{node_type} {{{', '.join(prop_list)}}}\n"
            
            # Add relationships
            schema += "\nThe relationships:\n"
            for rel in rel_types:
                source = rel.get("sourceNodeType", "").replace(":`", "").replace("`", "")
                target = rel.get("targetNodeType", "").replace(":`", "").replace("`", "")
                rel_type = rel.get("relType", "")
                
                # Skip internal node types
                if source.startswith("__") or target.startswith("__") or not source or not target:
                    continue
                    
                schema += f"(:{source})-[:{rel_type}]->(:{target})\n"
                
            return schema
            
        except Exception as e:
            logger.warning(f"Error generating schema: {str(e)}")
            # Use the fallback schema from domain config
            domain_config = self.settings.domain_prompts
            if hasattr(self.settings, 'fallback_schema'):
                return self.settings.fallback_schema
            
            # For backward compatibility
            return domain_config.get("fallback_schema", """
            Node properties:
            Feature {name: STRING, description: STRING, category: STRING}
            Process {name: STRING, description: STRING}
            Task {name: STRING, description: STRING}
            Role {name: STRING, description: STRING}
            Chunk {text: STRING, index: INTEGER}
            
            The relationships:
            (:Process)-[:HAS_STEP]->(:Task)
            (:Feature)-[:REQUIRES]->(:Feature)
            (:Task)-[:PERFORMED_BY]->(:Role)
            (:Feature)-[:PART_OF]->(:Feature)
            (:Chunk)-[:NEXT_CHUNK]->(:Chunk)
            """)
            
    def _get_node_types_fallback(self, session) -> List[Dict[str, Any]]:
        """Fallback method to get node types and properties"""
        result = []
        
        # Get all node labels
        labels = session.run("CALL db.labels()").data()
        
        for label_record in labels:
            label = label_record.get("label")
            if label:
                # For each label, get a sample node and its properties
                properties_query = f"""
                MATCH (n:`{label}`) 
                RETURN keys(n) as properties 
                LIMIT 1
                """
                
                properties_result = session.run(properties_query).data()
                properties = properties_result[0].get("properties", []) if properties_result else []
                
                result.append({
                    "nodeType": label,
                    "properties": properties
                })
                
        return result
        
    def _get_rel_types_fallback(self, session) -> List[Dict[str, Any]]:
        """Fallback method to get relationship types"""
        result = []
        
        # Get relationship types
        rel_types = session.run("CALL db.relationshipTypes()").data()
        
        for rel_record in rel_types:
            rel_type = rel_record.get("relationshipType")
            if rel_type:
                # For each relationship type, get a sample and its connected nodes
                rel_query = f"""
                MATCH (a)-[r:`{rel_type}`]->(b)
                RETURN labels(a) as source, labels(b) as target, keys(r) as properties
                LIMIT 1
                """
                
                rel_result = session.run(rel_query).data()
                
                if rel_result:
                    source = rel_result[0].get("source", [])[0] if rel_result[0].get("source") else ""
                    target = rel_result[0].get("target", [])[0] if rel_result[0].get("target") else ""
                    properties = rel_result[0].get("properties", [])
                    
                    result.append({
                        "sourceNodeType": source,
                        "relType": rel_type,
                        "targetNodeType": target,
                        "properties": properties
                    })
                
        return result
        
    def retrieve(
        self, 
        query: str, 
        top_k: Optional[int] = None, 
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context by directly querying the knowledge graph.
        
        Args:
            query: The query text
            top_k: Number of results to retrieve (not used for kg retrieval)
            **kwargs: Additional keyword arguments
            
        Returns:
            List of retrieved context items
        """
        try:
            # Execute the Text2Cypher retrieval
            retriever_result = self.kg_retriever.search(query_text=query)
            
            # The result contains the generated Cypher query and its results
            cypher_query = retriever_result.cypher_query
            query_results = retriever_result.records
            
            # Format results as a single dictionary
            result = {
                "cypher_query": cypher_query,
                "results": query_results,
            }
            
            return [result]
        except Exception as e:
            logger.error(f"Error in knowledge graph retrieval: {str(e)}")
            # Return empty results on error
            return []
            
    def answer_question(
        self, 
        query: str, 
        top_k: Optional[int] = None, 
        **kwargs
    ) -> QueryResponse:
        """
        Answer a question using knowledge graph retrieval.
        
        Args:
            query: The question to answer
            top_k: Number of results to retrieve (not used for kg retrieval)
            **kwargs: Additional keyword arguments
            
        Returns:
            Query response with answer and context
        """
        start_time = time.time()
        
        try:
            # Create GraphRAG pipeline for knowledge graph retrieval
            rag = GraphRAG(
                retriever=self.kg_retriever, 
                llm=self.llm,
                prompt_template=self.prompt_template
            )

            # Run the RAG pipeline
            rag_result = rag.search(query_text=query)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Parse entity and relationship data from retrieval context
            entities = []
            relationships = []
            raw_results = []
            
            # Extract raw results and generated Cypher query
            if hasattr(rag_result, "retrieval_context"):
                for item in rag_result.retrieval_context:
                    if isinstance(item, dict):
                        # Add to raw results
                        raw_results.append(item)
                        
                        # Extract node data
                        for key, value in item.items():
                            # Try to determine if this is an entity by checking for labels
                            if isinstance(value, dict) and "labels" in value:
                                try:
                                    entity = Entity(
                                        labels=value.get("labels", []),
                                        properties=value.get("properties", {}),
                                        node_id=value.get("id")
                                    )
                                    entities.append(entity)
                                except Exception:
                                    pass
            
            # Create KG query result
            kg_result = KnowledgeGraphQueryResult(
                query=getattr(rag_result, "cypher_query", ""),
                entities=entities,
                relationships=relationships,
                raw_results=raw_results
            )
            
            # Create response
            return QueryResponse(
                query=query,
                answer=rag_result.answer,
                retrieval_method="kg",
                query_time=response_time,
                context=kg_result,
            )
        except Exception as e:
            logger.error(f"Error answering question with knowledge graph retrieval: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Calculate response time even for errors
            response_time = time.time() - start_time
            
            # Return error response
            return QueryResponse(
                query=query,
                answer=f"Error retrieving answer: {str(e)}",
                retrieval_method="kg",
                query_time=response_time,
                context=None,
                metadata={"error": str(e)},
            )