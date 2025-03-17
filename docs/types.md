# Types — neo4j-graphrag-python documentation

## RawSearchResult

_class_ `neo4j_graphrag.types.RawSearchResult(*args, records, metadata=None)`
[[source]](./modules/neo4j_graphrag/types.html#RawSearchResult)

Represents the raw result returned from the retriever get_search_result method. It needs to be formatted further before being returned as a RetrieverResult.

Parameters:

* **records** ([list][https://docs.python.org/3/library/stdtypes.html#list](Record))
* **metadata** ([dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any) | None)

### Attributes

**records**
A list of records from neo4j.
Type: [list][https://docs.python.org/3/library/stdtypes.html#list](neo4j.Record)

**metadata**
Record-related metadata, such as score.
Type: [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any) | None

## RetrieverResult

_class_ `neo4j_graphrag.types.RetrieverResult(*args, items, metadata=None)`
[[source]](./modules/neo4j_graphrag/types.html#RetrieverResult)

Represents a result returned from a retriever.

Parameters:

* **items** ([list][https://docs.python.org/3/library/stdtypes.html#list](RetrieverResultItem))
* **metadata** ([dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any) | None)

### Attributes

**items**
A list of retrieved items.
Type: [list][https://docs.python.org/3/library/stdtypes.html#list](RetrieverResultItem)

**metadata**
Context-related metadata such as generated Cypher query in the Text2CypherRetriever.
Type: [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any) | None

## RetrieverResultItem

_class_ `neo4j_graphrag.types.RetrieverResultItem(*args, content, metadata=None)`
[[source]](./modules/neo4j_graphrag/types.html#RetrieverResultItem)

A single record returned from a retriever.

Parameters:

* **content** ([Any](https://docs.python.org/3/library/typing.html#typing.Any))
* **metadata** ([dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any) | None)

### Attributes

**content**
The context as will be provided to the LLM
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**metadata**
Any metadata that can be included together with the text, related to that record (e.g. another node property)
Type: Optional[[dict](https://docs.python.org/3/library/stdtypes.html#dict)]

## LLMResponse

_class_ `neo4j_graphrag.llm.types.LLMResponse(*args, content)`
[[source]](./modules/neo4j_graphrag/llm/types.html#LLMResponse)

Parameters:

* **content** ([str](https://docs.python.org/3/library/stdtypes.html#str))

## LLMMessage

_class_ `neo4j_graphrag.types.LLMMessage`
[[source]](./modules/neo4j_graphrag/types.html#LLMMessage)

## RagResultModel

_class_ `neo4j_graphrag.generation.types.RagResultModel(*args, answer, retriever_result=None)`
[[source]](./modules/neo4j_graphrag/generation/types.html#RagResultModel)

Parameters:

* **answer** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **retriever_result** (RetrieverResult | None)

## DocumentInfo

_class_ `neo4j_graphrag.experimental.components.types.DocumentInfo(*args, path, metadata=None, uid=<factory>)`
[[source]](./modules/neo4j_graphrag/experimental/components/types.html#DocumentInfo)

A document loaded by a DataLoader.

Parameters:

* **path** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **metadata** ([Dict][https://docs.python.org/3/library/typing.html#typing.Dict](str, str) | None)
* **uid** ([str](https://docs.python.org/3/library/stdtypes.html#str))

### Attributes

**path**
Document path.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**metadata**
Metadata associated with this document.
Type: Optional[[dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)]

**uid**
Unique identifier for this document.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

## TextChunk

_class_ `neo4j_graphrag.experimental.components.types.TextChunk(*args, text, index, metadata=None, uid=<factory>)`
[[source]](./modules/neo4j_graphrag/experimental/components/types.html#TextChunk)

A chunk of text split from a document by a text splitter.

Parameters:

* **text** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **index** ([int](https://docs.python.org/3/library/functions.html#int))
* **metadata** ([dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any) | None)
* **uid** ([str](https://docs.python.org/3/library/stdtypes.html#str))

### Attributes

**text**
The raw chunk text.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**index**
The position of this chunk in the original document.
Type: [int](https://docs.python.org/3/library/functions.html#int)

**metadata**
Metadata associated with this chunk.
Type: Optional[[dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)]

**uid**
Unique identifier for this chunk.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

## TextChunks

_class_ `neo4j_graphrag.experimental.components.types.TextChunks(*args, chunks)`
[[source]](./modules/neo4j_graphrag/experimental/components/types.html#TextChunks)

A collection of text chunks returned from a text splitter.

Parameters:

* **chunks** ([list][https://docs.python.org/3/library/stdtypes.html#list](TextChunk))

### Attributes

**chunks**
A list of text chunks.
Type: [list][https://docs.python.org/3/library/stdtypes.html#list](TextChunk)

## Neo4jNode

_class_ `neo4j_graphrag.experimental.components.types.Neo4jNode(*args, id, label, properties={}, embedding_properties=None)`
[[source]](./modules/neo4j_graphrag/experimental/components/types.html#Neo4jNode)

Represents a Neo4j node.

Parameters:

* **id** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **label** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **properties** ([dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any))
* **embedding_properties** ([dict][https://docs.python.org/3/library/stdtypes.html#dict](str, list[float)] | None)

### Attributes

**id**
The element ID of the node.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**label**
The label of the node.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**properties**
A dictionary of properties attached to the node.
Type: [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)

**embedding_properties**
A list of embedding properties attached to the node.
Type: Optional[[dict][https://docs.python.org/3/library/stdtypes.html#dict](str, [list)[https://docs.python.org/3/library/stdtypes.html#list](float)]]

## Neo4jRelationship

_class_ `neo4j_graphrag.experimental.components.types.Neo4jRelationship(*args, start_node_id, end_node_id, type, properties={}, embedding_properties=None)`
[[source]](./modules/neo4j_graphrag/experimental/components/types.html#Neo4jRelationship)

Represents a Neo4j relationship.

Parameters:

* **start_node_id** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **end_node_id** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **type** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **properties** ([dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any))
* **embedding_properties** ([dict][https://docs.python.org/3/library/stdtypes.html#dict](str, [list)[https://docs.python.org/3/library/stdtypes.html#list](float)] | None)

### Attributes

**start_node_id**
The ID of the start node.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**end_node_id**
The ID of the end node.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**type**
The relationship type.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**properties**
A dictionary of properties attached to the relationship.
Type: [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)

**embedding_properties**
A list of embedding properties attached to the relationship.
Type: Optional[[dict][https://docs.python.org/3/library/stdtypes.html#dict](str, [list)[https://docs.python.org/3/library/stdtypes.html#list](float)]]

## Neo4jGraph

_class_ `neo4j_graphrag.experimental.components.types.Neo4jGraph(*args, nodes=[], relationships=[])`
[[source]](./modules/neo4j_graphrag/experimental/components/types.html#Neo4jGraph)

Represents a Neo4j graph.

Parameters:

* **nodes** ([list][https://docs.python.org/3/library/stdtypes.html#list](Neo4jNode))
* **relationships** ([list][https://docs.python.org/3/library/stdtypes.html#list](Neo4jRelationship))

### Attributes

**nodes**
A list of nodes in the graph.
Type: [list][https://docs.python.org/3/library/stdtypes.html#list](Neo4jNode)

**relationships**
A list of relationships in the graph.
Type: [list][https://docs.python.org/3/library/stdtypes.html#list](Neo4jRelationship)

## KGWriterModel

_class_ `neo4j_graphrag.experimental.components.kg_writer.KGWriterModel(*args, status, metadata=None)`
[[source]](./modules/neo4j_graphrag/experimental/components/kg_writer.html#KGWriterModel)

Data model for the output of the Knowledge Graph writer.

Parameters:

* **status** ([Literal][https://docs.python.org/3/library/typing.html#typing.Literal]('SUCCESS', 'FAILURE'))
* **metadata** ([dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any) | None)

### Attributes

**status**
Whether the write operation was successful.
Type: Literal["SUCCESS", "FAILURE"]

## SchemaProperty

_class_ `neo4j_graphrag.experimental.components.schema.SchemaProperty(*args, name, type, description='')`
[[source]](./modules/neo4j_graphrag/experimental/components/schema.html#SchemaProperty)

Represents a property on a node or relationship in the graph.

Parameters:

* **name** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **type** ([Literal][https://docs.python.org/3/library/typing.html#typing.Literal]('BOOLEAN', 'DATE', 'DURATION', 'FLOAT', 'INTEGER', 'LIST', 'LOCAL_DATETIME', 'LOCAL_TIME', 'POINT', 'STRING', 'ZONED_DATETIME', 'ZONED_TIME'))
* **description** ([str](https://docs.python.org/3/library/stdtypes.html#str))

### Attributes

**name**
The name of the property.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**type**
The type of the property.
Type: Literal['BOOLEAN', 'DATE', 'DURATION', 'FLOAT', 'INTEGER', 'LIST', 'LOCAL_DATETIME', 'LOCAL_TIME', 'POINT', 'STRING', 'ZONED_DATETIME', 'ZONED_TIME']

**description**
The description of the property.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

## SchemaEntity

_class_ `neo4j_graphrag.experimental.components.schema.SchemaEntity(*args, label, description='', properties=[])`
[[source]](./modules/neo4j_graphrag/experimental/components/schema.html#SchemaEntity)

Represents a possible node in the graph.

Parameters:

* **label** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **description** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **properties** ([List][https://docs.python.org/3/library/typing.html#typing.List](SchemaProperty))

### Attributes

**label**
The label of the entity.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**description**
The description of the entity.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**properties**
A list of properties attached to the entity.
Type: [List][https://docs.python.org/3/library/typing.html#typing.List](SchemaProperty)

## SchemaRelation

_class_ `neo4j_graphrag.experimental.components.schema.SchemaRelation(*args, label, description='', properties=[])`
[[source]](./modules/neo4j_graphrag/experimental/components/schema.html#SchemaRelation)

Represents a possible relationship between nodes in the graph.

Parameters:

* **label** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **description** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **properties** ([List][https://docs.python.org/3/library/typing.html#typing.List](SchemaProperty))

### Attributes

**label**
The label of the relationship.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**description**
The description of the relationship.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**properties**
A list of properties attached to the relationship.
Type: [List][https://docs.python.org/3/library/typing.html#typing.List](SchemaProperty)

## SchemaConfig

_class_ `neo4j_graphrag.experimental.components.schema.SchemaConfig(*args, entities, relations, potential_schema)`
[[source]](./modules/neo4j_graphrag/experimental/components/schema.html#SchemaConfig)

Represents possible relationships between entities and relations in the graph.

Parameters:

* **entities** ([Dict][https://docs.python.org/3/library/typing.html#typing.Dict](str, Dict[str, Any)])
* **relations** ([Dict][https://docs.python.org/3/library/typing.html#typing.Dict](str, Dict[str, Any)] | None)
* **potential_schema** ([List][https://docs.python.org/3/library/typing.html#typing.List](Tuple[str, str, str)] | None)

### Attributes

**entities**
A dictionary of entities in the graph.
Type: [Dict][https://docs.python.org/3/library/typing.html#typing.Dict](str, Dict[str, Any)]

**relations**
A dictionary of relations in the graph.
Type: [Dict][https://docs.python.org/3/library/typing.html#typing.Dict](str, Dict[str, Any)] | None

**potential_schema**
A list of potential schema configurations.
Type: [List][https://docs.python.org/3/library/typing.html#typing.List](Tuple[str, str, str)] | None

## LexicalGraphConfig

_class_ `neo4j_graphrag.experimental.components.types.LexicalGraphConfig(*args, id_prefix='', document_node_label='Document', chunk_node_label='Chunk', chunk_to_document_relationship_type='FROM_DOCUMENT', next_chunk_relationship_type='NEXT_CHUNK', node_to_chunk_relationship_type='FROM_CHUNK', chunk_id_property='id', chunk_index_property='index', chunk_text_property='text', chunk_embedding_property='embedding')`
[[source]](./modules/neo4j_graphrag/experimental/components/types.html#LexicalGraphConfig)

Configure all labels and property names in the lexical graph.

Parameters:

* **id_prefix** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **document_node_label** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **chunk_node_label** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **chunk_to_document_relationship_type** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **next_chunk_relationship_type** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **node_to_chunk_relationship_type** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **chunk_id_property** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **chunk_index_property** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **chunk_text_property** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **chunk_embedding_property** ([str](https://docs.python.org/3/library/stdtypes.html#str))

### Attributes

**id_prefix**
The prefix for all IDs in the graph.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**document_node_label**
The label for document nodes.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**chunk_node_label**
The label for chunk nodes.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**chunk_to_document_relationship_type**
The type for relationships from chunks to documents.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**next_chunk_relationship_type**
The type for relationships between chunks.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**node_to_chunk_relationship_type**
The type for relationships from nodes to chunks.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**chunk_id_property**
The property for the ID of a chunk.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**chunk_index_property**
The property for the index of a chunk.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**chunk_text_property**
The property for the text of a chunk.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**chunk_embedding_property**
The property for the embedding of a chunk.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

## Neo4jDriverType

_class_ `neo4j_graphrag.experimental.pipeline.config.object_config.Neo4jDriverType(root=PydanticUndefined)`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/config/object_config.html#Neo4jDriverType)

A model to wrap neo4j.Driver and Neo4jDriverConfig objects.

The parse method always returns a neo4j.Driver.

Parameters:

* **root** (Driver | [Neo4jDriverConfig](#neo4j_graphrag.experimental.pipeline.config.object_config.Neo4jDriverConfig "neo4j_graphrag.experimental.pipeline.config.object_config.Neo4jDriverConfig"))

### Attributes

**root**
The root object to wrap.
Type: Driver | [Neo4jDriverConfig](#neo4j_graphrag.experimental.pipeline.config.object_config.Neo4jDriverConfig "neo4j_graphrag.experimental.pipeline.config.object_config.Neo4jDriverConfig")

## Neo4jDriverConfig

_class_ `neo4j_graphrag.experimental.pipeline.config.object_config.Neo4jDriverConfig(*args, class_=None, params_={})`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/config/object_config.html#Neo4jDriverConfig)

Parameters:

* **class_** ([str](https://docs.python.org/3/library/stdtypes.html#str) | None)
* **params_** ([dict](https://docs.python.org/3/library/stdtypes.html#dict)[str, float | str | [ParamFromEnvConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig") | [ParamFromKeyConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig") | [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)])

### Attributes

**class_**
The class of the driver.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str) | None

**params_**
The parameters for the driver.
Type: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[str, float | str | [ParamFromEnvConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig") | [ParamFromKeyConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig") | [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)]

## LLMType

_class_ `neo4j_graphrag.experimental.pipeline.config.object_config.LLMType(root=PydanticUndefined)`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/config/object_config.html#LLMType)

A model to wrap LLMInterface and LLMConfig objects.

The parse method always returns an object inheriting from LLMInterface.

Parameters:

* **root** ([LLMInterface](about:blank/api.html#neo4j_graphrag.llm.base.LLMInterface) | [LLMConfig](#neo4j_graphrag.experimental.pipeline.config.object_config.LLMConfig "neo4j_graphrag.experimental.pipeline.config.object_config.LLMConfig"))

### Attributes

**root**
The root object to wrap.
Type: [LLMInterface](about:blank/api.html#neo4j_graphrag.llm.base.LLMInterface) | [LLMConfig](#neo4j_graphrag.experimental.pipeline.config.object_config.LLMConfig "neo4j_graphrag.experimental.pipeline.config.object_config.LLMConfig")

## LLMConfig

_class_ `neo4j_graphrag.experimental.pipeline.config.object_config.LLMConfig(*args, class_=None, params_={})`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/config/object_config.html#LLMConfig)

Configuration for any LLMInterface object.

By default, will try to import from neo4j_graphrag.llm.

Parameters:

* **class_** ([str](https://docs.python.org/3/library/stdtypes.html#str) | None)
* **params_** ([dict](https://docs.python.org/3/library/stdtypes.html#dict)[str, float | str | [ParamFromEnvConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig") | [ParamFromKeyConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig") | [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)])

### Attributes

**class_**
The class of the LLMInterface.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str) | None

**params_**
The parameters for the LLMInterface.
Type: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[str, float | str | [ParamFromEnvConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig") | [ParamFromKeyConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig") | [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)]

## EmbedderType

_class_ `neo4j_graphrag.experimental.pipeline.config.object_config.EmbedderType(root=PydanticUndefined)`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/config/object_config.html#EmbedderType)

A model to wrap Embedder and EmbedderConfig objects.

The parse method always returns an object inheriting from Embedder.

Parameters:

* **root** ([Embedder](about:blank/api.html#neo4j_graphrag.embeddings.base.Embedder) | [EmbedderConfig](#neo4j_graphrag.experimental.pipeline.config.object_config.EmbedderConfig "neo4j_graphrag.experimental.pipeline.config.object_config.EmbedderConfig"))

### Attributes

**root**
The root object to wrap.
Type: [Embedder](about:blank/api.html#neo4j_graphrag.embeddings.base.Embedder) | [EmbedderConfig](#neo4j_graphrag.experimental.pipeline.config.object_config.EmbedderConfig "neo4j_graphrag.experimental.pipeline.config.object_config.EmbedderConfig")

## EmbedderConfig

_class_ `neo4j_graphrag.experimental.pipeline.config.object_config.EmbedderConfig(*args, class_=None, params_={})`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/config/object_config.html#EmbedderConfig)

Configuration for any Embedder object.

By default, will try to import from neo4j_graphrag.embeddings.

Parameters:

* **class_** ([str](https://docs.python.org/3/library/stdtypes.html#str) | None)
* **params_** ([dict](https://docs.python.org/3/library/stdtypes.html#dict)[str, float | str | [ParamFromEnvConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig") | [ParamFromKeyConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig") | [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)])

### Attributes

**class_**
The class of the Embedder.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str) | None

**params_**
The parameters for the Embedder.
Type: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[str, float | str | [ParamFromEnvConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig") | [ParamFromKeyConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig") | [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)]

## ComponentType

_class_ `neo4j_graphrag.experimental.pipeline.config.object_config.ComponentType(root=PydanticUndefined)`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/config/object_config.html#ComponentType)

Parameters:

* **root** (Component | [ComponentConfig](#neo4j_graphrag.experimental.pipeline.config.object_config.ComponentConfig "neo4j_graphrag.experimental.pipeline.config.object_config.ComponentConfig"))

### Attributes

**root**
The root object to wrap.
Type: Component | [ComponentConfig](#neo4j_graphrag.experimental.pipeline.config.object_config.ComponentConfig "neo4j_graphrag.experimental.pipeline.config.object_config.ComponentConfig")

## ComponentConfig

_class_ `neo4j_graphrag.experimental.pipeline.config.object_config.ComponentConfig(*args, class_=None, params_={}, run_params_={})`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/config/object_config.html#ComponentConfig)

A config model for all components.

In addition to the object config, components can have pre-defined parameters that will be passed to the run method, ie run_params_.

Parameters:

* **class_** ([str](https://docs.python.org/3/library/stdtypes.html#str) | None)
* **params_** ([dict](https://docs.python.org/3/library/stdtypes.html#dict)[str, float | str | [ParamFromEnvConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig") | [ParamFromKeyConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig") | [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)])
* **run_params_** ([dict](https://docs.python.org/3/library/stdtypes.html#dict)[str, float | str | [ParamFromEnvConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig") | [ParamFromKeyConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig") | [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)])

### Attributes

**class_**
The class of the component.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str) | None

**params_**
The parameters for the component.
Type: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[str, float | str | [ParamFromEnvConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig") | [ParamFromKeyConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig") | [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)]

**run_params_**
The run parameters for the component.
Type: [dict](https://docs.python.org/3/library/stdtypes.html#dict)[str, float | str | [ParamFromEnvConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig") | [ParamFromKeyConfig](#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromKeyConfig") | [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any)]

## ParamFromEnvConfig

_class_ `neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig(*args, resolver_=ParamResolverEnum.ENV_, var__)`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/config/param_resolver.html#ParamFromEnvConfig)

Parameters:

* **resolver_** ([Literal][https://docs.python.org/3/library/typing.html#typing.Literal](**ParamResolverEnum.ENV**))
* **var_** ([str](https://docs.python.org/3/library/stdtypes.html#str))

### Attributes

**resolver_**
The resolver for the parameter.
Type: Literal[**ParamResolverEnum.ENV**]

**var_**
The variable for the parameter.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

## EventType

_enum_ `neo4j_graphrag.experimental.pipeline.types.EventType(value)`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/types.html#EventType)

Valid values are as follows:

PIPELINE_STARTED = <EventType.PIPELINE_STARTED: 'PIPELINE_STARTED'>

TASK_STARTED = <EventType.TASK_STARTED: 'TASK_STARTED'>

TASK_FINISHED = <EventType.TASK_FINISHED: 'TASK_FINISHED'>

PIPELINE_FINISHED = <EventType.PIPELINE_FINISHED: 'PIPELINE_FINISHED'>

## PipelineEvent

_class_ `neo4j_graphrag.experimental.pipeline.types.PipelineEvent(*args, event_type, run_id, timestamp=<factory>, message=None, payload=None)`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/types.html#PipelineEvent)

Parameters:

* **event_type** ([EventType](#neo4j_graphrag.experimental.pipeline.types.EventType "neo4j_graphrag.experimental.pipeline.types.EventType"))
* **run_id** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **timestamp** ([datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "(in Python v3.13)"))
* **message** ([str](https://docs.python.org/3/library/stdtypes.html#str) | None)
* **payload** ([dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any) | None)

### Attributes

**event_type**
The type of the event.
Type: [EventType](#neo4j_graphrag.experimental.pipeline.types.EventType "neo4j_graphrag.experimental.pipeline.types.EventType")

**run_id**
The ID of the run.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**timestamp**
The timestamp of the event.
Type: [datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "(in Python v3.13)"))

**message**
The message of the event.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str) | None

**payload**
The payload of the event.
Type: [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any) | None

## TaskEvent

_class_ `neo4j_graphrag.experimental.pipeline.types.TaskEvent(*args, event_type, run_id, timestamp=<factory>, message=None, payload=None, task_name)`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/types.html#TaskEvent)

Parameters:

* **event_type** ([EventType](#neo4j_graphrag.experimental.pipeline.types.EventType "neo4j_graphrag.experimental.pipeline.types.EventType"))
* **run_id** ([str](https://docs.python.org/3/library/stdtypes.html#str))
* **timestamp** ([datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "(in Python v3.13)"))
* **message** ([str](https://docs.python.org/3/library/stdtypes.html#str) | None)
* **payload** ([dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any) | None)
* **task_name** ([str](https://docs.python.org/3/library/stdtypes.html#str))

### Attributes

**event_type**
The type of the event.
Type: [EventType](#neo4j_graphrag.experimental.pipeline.types.EventType "neo4j_graphrag.experimental.pipeline.types.EventType")

**run_id**
The ID of the run.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

**timestamp**
The timestamp of the event.
Type: [datetime](https://docs.python.org/3/library/datetime.html#datetime.datetime "(in Python v3.13)"))

**message**
The message of the event.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str) | None

**payload**
The payload of the event.
Type: [dict][https://docs.python.org/3/library/stdtypes.html#dict](str, Any) | None

**task_name**
The name of the task.
Type: [str](https://docs.python.org/3/library/stdtypes.html#str)

## EventCallbackProtocol

_class_ `neo4j_graphrag.experimental.pipeline.types.EventCallbackProtocol(*args, **kwargs)`
[[source]](./modules/neo4j_graphrag/experimental/pipeline/types.html#EventCallbackProtocol)

**call**(event)
[[source]](./modules/neo4j_graphrag/experimental/pipeline/types.html#EventCallbackProtocol.__call__)

Call self as a function.

Parameters:

* **event** (Event)

Return type:
[Awaitable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Awaitable "(in Python v3.13)")\[None\]
