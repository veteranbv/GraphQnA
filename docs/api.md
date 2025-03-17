# API Documentation — neo4j-graphrag-python  documentation

Components
-------------------------------------------------

### DataLoader

_class_ neo4j\_graphrag.experimental.components.pdf\_loader.DataLoader[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/pdf_loader.html#DataLoader)

Interface for loading data of various input types.

get\_document\_metadata(_text_, _metadata\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/pdf_loader.html#DataLoader.get_document_metadata)

Parameters:

* **text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **metadata** ([_Dict_](https://docs.python.org/3/library/typing.html#typing.Dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_ _|_ _None_)

Return type:

[_Dict_](https://docs.python.org/3/library/typing.html#typing.Dict "(in Python v3.13)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"), [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")\] | None

_abstract async_ run(_filepath_, _metadata\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/pdf_loader.html#DataLoader.run)

Parameters:

* **filepath** ([_Path_](https://docs.python.org/3/library/pathlib.html#pathlib.Path "(in Python v3.13)"))

* **metadata** ([_Dict_](https://docs.python.org/3/library/typing.html#typing.Dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_ _|_ _None_)

Return type:

_PdfDocument_

### PdfLoader

_class_ neo4j\_graphrag.experimental.components.pdf\_loader.PdfLoader[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/pdf_loader.html#PdfLoader)

_static_ load\_file(_file_, _fs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/pdf_loader.html#PdfLoader.load_file)

Parse PDF file and return text.

Parameters:

* **file** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **fs** (_AbstractFileSystem_)

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

_async_ run(_filepath_, _metadata\=None_, _fs\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/pdf_loader.html#PdfLoader.run)

Parameters:

* **filepath** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)") _|_ [_Path_](https://docs.python.org/3/library/pathlib.html#pathlib.Path "(in Python v3.13)"))

* **metadata** ([_Dict_](https://docs.python.org/3/library/typing.html#typing.Dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_ _|_ _None_)

* **fs** (_AbstractFileSystem_ _|_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)") _|_ _None_)

Return type:

_PdfDocument_

### TextSplitter

_class_ neo4j\_graphrag.experimental.components.text\_splitters.base.TextSplitter[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/text_splitters/base.html#TextSplitter)

Interface for a text splitter.

_abstract async_ run(_text_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/text_splitters/base.html#TextSplitter.run)

Splits a piece of text into chunks.

Parameters:

**text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to be split.

Returns:

A list of chunks.

Return type:

[TextChunks](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunks "neo4j_graphrag.experimental.components.types.TextChunks")

### FixedSizeSplitter

_class_ neo4j\_graphrag.experimental.components.text\_splitters.fixed\_size\_splitter.FixedSizeSplitter(_chunk\_size\=4000_, _chunk\_overlap\=200_, _approximate\=True_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/text_splitters/fixed_size_splitter.html#FixedSizeSplitter)

Text splitter which splits the input text into fixed or approximate fixed size

chunks with optional overlap.

Parameters:

* **chunk\_size** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – The number of characters in each chunk.

* **chunk\_overlap** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – The number of characters from the previous chunk to overlap with each chunk. Must be less than chunk\_size.

* **approximate** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")) – If True, avoids splitting words in the middle at chunk boundaries. Defaults to True.

Example:

```
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter
from neo4j_graphrag.experimental.pipeline import Pipeline

pipeline = Pipeline()
text_splitter = FixedSizeSplitter(chunk_size=4000, chunk_overlap=200, approximate=True)
pipeline.add_component(text_splitter, "text_splitter")

```

_async_ run(_text_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/text_splitters/fixed_size_splitter.html#FixedSizeSplitter.run)

Splits a piece of text into chunks.

Parameters:

**text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to be split.

Returns:

A list of chunks.

Return type:

[TextChunks](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunks "neo4j_graphrag.experimental.components.types.TextChunks")

### LangChainTextSplitterAdapter

_class_ neo4j\_graphrag.experimental.components.text\_splitters.langchain.LangChainTextSplitterAdapter(_text\_splitter_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/text_splitters/langchain.html#LangChainTextSplitterAdapter)

Adapter for LangChain TextSplitters. Allows instances of this class to be used in the knowledge graph builder pipeline.

Parameters:

**text\_splitter** (_LangChainTextSplitter_) – An instance of LangChain’s TextSplitter class.

Example:

```
from langchain_text_splitters import RecursiveCharacterTextSplitter
from neo4j_graphrag.experimental.components.text_splitters.langchain import LangChainTextSplitterAdapter
from neo4j_graphrag.experimental.pipeline import Pipeline

pipeline = Pipeline()
text_splitter = LangChainTextSplitterAdapter(RecursiveCharacterTextSplitter())
pipeline.add_component(text_splitter, "text_splitter")

```

_async_ run(_text_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/text_splitters/langchain.html#LangChainTextSplitterAdapter.run)

Splits text into chunks.

Parameters:

**text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to split.

Returns:

The text split into chunks.

Return type:

[TextChunks](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunks "neo4j_graphrag.experimental.components.types.TextChunks")

### LlamaIndexTextSplitterAdapter

_class_ neo4j\_graphrag.experimental.components.text\_splitters.llamaindex.LlamaIndexTextSplitterAdapter(_text\_splitter_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/text_splitters/llamaindex.html#LlamaIndexTextSplitterAdapter)

Adapter for LlamaIndex TextSplitters. Allows instances of this class to be used in the knowledge graph builder pipeline.

Parameters:

**text\_splitter** (_LlamaIndexTextSplitter_) – An instance of LlamaIndex’s TextSplitter class.

Example:

```
from llama_index.core.node_parser.text.sentence import SentenceSplitter
from neo4j_graphrag.experimental.components.text_splitters.llamaindex import (
    LlamaIndexTextSplitterAdapter,
)
from neo4j_graphrag.experimental.pipeline import Pipeline

pipeline = Pipeline()
text_splitter = LlamaIndexTextSplitterAdapter(SentenceSplitter())
pipeline.add_component(text_splitter, "text_splitter")

```

_async_ run(_text_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/text_splitters/llamaindex.html#LlamaIndexTextSplitterAdapter.run)

Splits text into chunks.

Parameters:

**text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to split.

Returns:

The text split into chunks.

Return type:

[TextChunks](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunks "neo4j_graphrag.experimental.components.types.TextChunks")

### TextChunkEmbedder

_class_ neo4j\_graphrag.experimental.components.embedder.TextChunkEmbedder(_embedder_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/embedder.html#TextChunkEmbedder)

Component for creating embeddings from text chunks.

Parameters:

**embedder** ([_Embedder_](#neo4j_graphrag.embeddings.base.Embedder "neo4j_graphrag.embeddings.base.Embedder")) – The embedder to use to create the embeddings.

Example:

```
from neo4j_graphrag.experimental.components.embedder import TextChunkEmbedder
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
from neo4j_graphrag.experimental.pipeline import Pipeline

embedder = OpenAIEmbeddings(model="text-embedding-3-large")
chunk_embedder = TextChunkEmbedder(embedder)
pipeline = Pipeline()
pipeline.add_component(chunk_embedder, "chunk_embedder")

```

_async_ run(_text\_chunks_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/embedder.html#TextChunkEmbedder.run)

Embed a list of text chunks.

Parameters:

**text\_chunks** ([_TextChunks_](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunks "neo4j_graphrag.experimental.components.types.TextChunks")) – The text chunks to embed.

Returns:

The input text chunks with each one having an added embedding.

Return type:

[TextChunks](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunks "neo4j_graphrag.experimental.components.types.TextChunks")

### LexicalGraphBuilder

_class_ neo4j\_graphrag.experimental.components.lexical\_graph.LexicalGraphBuilder(_config\=LexicalGraphConfig(id\_prefix='', document\_node\_label='Document', chunk\_node\_label='Chunk', chunk\_to\_document\_relationship\_type='FROM\_DOCUMENT', next\_chunk\_relationship\_type='NEXT\_CHUNK', node\_to\_chunk\_relationship\_type='FROM\_CHUNK', chunk\_id\_property='id', chunk\_index\_property='index', chunk\_text\_property='text', chunk\_embedding\_property='embedding')_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/lexical_graph.html#LexicalGraphBuilder)

Builds the lexical graph to be inserted into neo4j. The lexical graph contains: - A node for each document - A node for each chunk - A relationship between each chunk and the document it was created from - A relationship between a chunk and the next one in the document

Parameters:

**config** ([_LexicalGraphConfig_](about:blank/types.html#neo4j_graphrag.experimental.components.types.LexicalGraphConfig "neo4j_graphrag.experimental.components.types.LexicalGraphConfig"))

_async_ run(_text\_chunks_, _document\_info\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/lexical_graph.html#LexicalGraphBuilder.run)

Parameters:

* **text\_chunks** ([_TextChunks_](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunks "neo4j_graphrag.experimental.components.types.TextChunks"))

* **document\_info** ([_DocumentInfo_](about:blank/types.html#neo4j_graphrag.experimental.components.types.DocumentInfo "neo4j_graphrag.experimental.components.types.DocumentInfo") _|_ _None_)

Return type:

_GraphResult_

_async_ process\_chunk(_graph_, _chunk_, _next\_chunk_, _document\_info\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/lexical_graph.html#LexicalGraphBuilder.process_chunk)

Add chunks and relationships between them (NEXT\_CHUNK)

Updates graph in place.

Parameters:

* **graph** ([_Neo4jGraph_](about:blank/types.html#neo4j_graphrag.experimental.components.types.Neo4jGraph "neo4j_graphrag.experimental.components.types.Neo4jGraph"))

* **chunk** ([_TextChunk_](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunk "neo4j_graphrag.experimental.components.types.TextChunk"))

* **next\_chunk** ([_TextChunk_](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunk "neo4j_graphrag.experimental.components.types.TextChunk") _|_ _None_)

* **document\_info** ([_DocumentInfo_](about:blank/types.html#neo4j_graphrag.experimental.components.types.DocumentInfo "neo4j_graphrag.experimental.components.types.DocumentInfo") _|_ _None_)

Return type:

None

create\_document\_node(_document\_info_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/lexical_graph.html#LexicalGraphBuilder.create_document_node)

Create a Document node with ‘path’ property. Any document metadata is also added as a node property.

Parameters:

**document\_info** ([_DocumentInfo_](about:blank/types.html#neo4j_graphrag.experimental.components.types.DocumentInfo "neo4j_graphrag.experimental.components.types.DocumentInfo"))

Return type:

[_Neo4jNode_](about:blank/types.html#neo4j_graphrag.experimental.components.types.Neo4jNode "neo4j_graphrag.experimental.components.types.Neo4jNode")

create\_chunk\_node(_chunk_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/lexical_graph.html#LexicalGraphBuilder.create_chunk_node)

Create chunk node with properties ‘text’, ‘index’ and any ‘metadata’ added during the process. Special case for the potential chunk embedding property that gets added as an embedding\_property

Parameters:

**chunk** ([_TextChunk_](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunk "neo4j_graphrag.experimental.components.types.TextChunk"))

Return type:

[_Neo4jNode_](about:blank/types.html#neo4j_graphrag.experimental.components.types.Neo4jNode "neo4j_graphrag.experimental.components.types.Neo4jNode")

create\_chunk\_to\_document\_rel(_chunk_, _document\_info_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/lexical_graph.html#LexicalGraphBuilder.create_chunk_to_document_rel)

Create the relationship between a chunk and the document it belongs to.

Parameters:

* **chunk** ([_TextChunk_](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunk "neo4j_graphrag.experimental.components.types.TextChunk"))

* **document\_info** ([_DocumentInfo_](about:blank/types.html#neo4j_graphrag.experimental.components.types.DocumentInfo "neo4j_graphrag.experimental.components.types.DocumentInfo"))

Return type:

[_Neo4jRelationship_](about:blank/types.html#neo4j_graphrag.experimental.components.types.Neo4jRelationship "neo4j_graphrag.experimental.components.types.Neo4jRelationship")

create\_next\_chunk\_relationship(_chunk_, _next\_chunk_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/lexical_graph.html#LexicalGraphBuilder.create_next_chunk_relationship)

Create relationship between a chunk and the next one

Parameters:

* **chunk** ([_TextChunk_](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunk "neo4j_graphrag.experimental.components.types.TextChunk"))

* **next\_chunk** ([_TextChunk_](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunk "neo4j_graphrag.experimental.components.types.TextChunk"))

Return type:

[_Neo4jRelationship_](about:blank/types.html#neo4j_graphrag.experimental.components.types.Neo4jRelationship "neo4j_graphrag.experimental.components.types.Neo4jRelationship")

create\_node\_to\_chunk\_rel(_node_, _chunk\_id_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/lexical_graph.html#LexicalGraphBuilder.create_node_to_chunk_rel)

Create relationship between a chunk and entities found in that chunk

Parameters:

* **node** ([_Neo4jNode_](about:blank/types.html#neo4j_graphrag.experimental.components.types.Neo4jNode "neo4j_graphrag.experimental.components.types.Neo4jNode"))

* **chunk\_id** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

Return type:

[_Neo4jRelationship_](about:blank/types.html#neo4j_graphrag.experimental.components.types.Neo4jRelationship "neo4j_graphrag.experimental.components.types.Neo4jRelationship")

Create relationship between Chunk and each entity extracted from it.

Updates chunk\_graph in place.

Parameters:

* **chunk\_graph** ([_Neo4jGraph_](about:blank/types.html#neo4j_graphrag.experimental.components.types.Neo4jGraph "neo4j_graphrag.experimental.components.types.Neo4jGraph"))

* **chunk** ([_TextChunk_](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunk "neo4j_graphrag.experimental.components.types.TextChunk"))

Return type:

None

### Neo4jChunkReader

_class_ neo4j\_graphrag.experimental.components.neo4j\_reader.Neo4jChunkReader(_driver_, _fetch\_embeddings\=False_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/neo4j_reader.html#Neo4jChunkReader)

Reads text chunks from a Neo4j database.

Parameters:

* **driver** (_neo4j.driver_) – The Neo4j driver to connect to the database.

* **fetch\_embeddings** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")) – If True, the embedding property is also returned. Default to False.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.experimental.components.neo4j_reader import Neo4jChunkReader

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")
DATABASE = "neo4j"

driver = GraphDatabase.driver(URI, auth=AUTH)
reader = Neo4jChunkReader(driver=driver, neo4j_database=DATABASE)
await reader.run()

```

_async_ run(_lexical\_graph\_config\=LexicalGraphConfig(id\_prefix='', document\_node\_label='Document', chunk\_node\_label='Chunk', chunk\_to\_document\_relationship\_type='FROM\_DOCUMENT', next\_chunk\_relationship\_type='NEXT\_CHUNK', node\_to\_chunk\_relationship\_type='FROM\_CHUNK', chunk\_id\_property='id', chunk\_index\_property='index', chunk\_text\_property='text', chunk\_embedding\_property='embedding')_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/neo4j_reader.html#Neo4jChunkReader.run)

Reads text chunks from a Neo4j database.

Parameters:

**lexical\_graph\_config** ([_LexicalGraphConfig_](about:blank/types.html#neo4j_graphrag.experimental.components.types.LexicalGraphConfig "neo4j_graphrag.experimental.components.types.LexicalGraphConfig")) – Node labels and relationship types for the lexical graph.

Return type:

[_TextChunks_](about:blank/types.html#neo4j_graphrag.experimental.components.types.TextChunks "neo4j_graphrag.experimental.components.types.TextChunks")

### SchemaBuilder

_class_ neo4j\_graphrag.experimental.components.schema.SchemaBuilder[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/schema.html#SchemaBuilder)

A builder class for constructing SchemaConfig objects from given entities, relations, and their interrelationships defined in a potential schema.

Example:

```
from neo4j_graphrag.experimental.components.schema import (
    SchemaBuilder,
    SchemaEntity,
    SchemaProperty,
    SchemaRelation,
)
from neo4j_graphrag.experimental.pipeline import Pipeline

entities = [
    SchemaEntity(
        label="PERSON",
        description="An individual human being.",
        properties=[
            SchemaProperty(
                name="name", type="STRING", description="The name of the person"
            )
        ],
    ),
    SchemaEntity(
        label="ORGANIZATION",
        description="A structured group of people with a common purpose.",
        properties=[
            SchemaProperty(
                name="name", type="STRING", description="The name of the organization"
            )
        ],
    ),
]
relations = [
    SchemaRelation(
        label="EMPLOYED_BY", description="Indicates employment relationship."
    ),
]
potential_schema = [
    ("PERSON", "EMPLOYED_BY", "ORGANIZATION"),
]
pipe = Pipeline()
schema_builder = SchemaBuilder()
pipe.add_component(schema_builder, "schema_builder")
pipe_inputs = {
    "schema": {
        "entities": entities,
        "relations": relations,
        "potential_schema": potential_schema,
    },
    ...
}
pipe.run(pipe_inputs)

```

_async_ run(_entities_, _relations\=None_, _potential\_schema\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/schema.html#SchemaBuilder.run)

Asynchronously constructs and returns a SchemaConfig object.

Parameters:

* **entities** (_List__\[_[_SchemaEntity_](about:blank/types.html#neo4j_graphrag.experimental.components.schema.SchemaEntity "neo4j_graphrag.experimental.components.schema.SchemaEntity")_\]_) – List of Entity objects.

* **relations** (_List__\[_[_SchemaRelation_](about:blank/types.html#neo4j_graphrag.experimental.components.schema.SchemaRelation "neo4j_graphrag.experimental.components.schema.SchemaRelation")_\]_) – List of Relation objects.

* **potential\_schema** (_Dict__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _List__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__\]_) – Dictionary mapping entity names to Lists of relation names.

Returns:

A configured schema object, constructed asynchronously.

Return type:

[SchemaConfig](about:blank/types.html#neo4j_graphrag.experimental.components.schema.SchemaConfig "neo4j_graphrag.experimental.components.schema.SchemaConfig")

### KGWriter

_class_ neo4j\_graphrag.experimental.components.kg\_writer.KGWriter[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/kg_writer.html#KGWriter)

Abstract class used to write a knowledge graph to a data store.

_abstract async_ run(_graph_, _lexical\_graph\_config\=LexicalGraphConfig(id\_prefix='', document\_node\_label='Document', chunk\_node\_label='Chunk', chunk\_to\_document\_relationship\_type='FROM\_DOCUMENT', next\_chunk\_relationship\_type='NEXT\_CHUNK', node\_to\_chunk\_relationship\_type='FROM\_CHUNK', chunk\_id\_property='id', chunk\_index\_property='index', chunk\_text\_property='text', chunk\_embedding\_property='embedding')_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/kg_writer.html#KGWriter.run)

Writes the graph to a data store.

Parameters:

* **graph** ([_Neo4jGraph_](about:blank/types.html#neo4j_graphrag.experimental.components.types.Neo4jGraph "neo4j_graphrag.experimental.components.types.Neo4jGraph")) – The knowledge graph to write to the data store.

* **lexical\_graph\_config** ([_LexicalGraphConfig_](about:blank/types.html#neo4j_graphrag.experimental.components.types.LexicalGraphConfig "neo4j_graphrag.experimental.components.types.LexicalGraphConfig")) – Node labels and relationship types in the lexical graph.

Return type:

[_KGWriterModel_](about:blank/types.html#neo4j_graphrag.experimental.components.kg_writer.KGWriterModel "neo4j_graphrag.experimental.components.kg_writer.KGWriterModel")

### Neo4jWriter

_class_ neo4j\_graphrag.experimental.components.kg\_writer.Neo4jWriter(_driver_, _neo4j\_database\=None_, _batch\_size\=1000_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/kg_writer.html#Neo4jWriter)

Writes a knowledge graph to a Neo4j database.

Parameters:

* **driver** (_neo4j.driver_) – The Neo4j driver to connect to the database.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

* **batch\_size** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – The number of nodes or relationships to write to the database in a batch. Defaults to 1000.

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.experimental.components.kg_writer import Neo4jWriter
from neo4j_graphrag.experimental.pipeline import Pipeline

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")
DATABASE = "neo4j"

driver = GraphDatabase.driver(URI, auth=AUTH)
writer = Neo4jWriter(driver=driver, neo4j_database=DATABASE)

pipeline = Pipeline()
pipeline.add_component(writer, "writer")

```

_async_ run(_graph_, _lexical\_graph\_config\=LexicalGraphConfig(id\_prefix='', document\_node\_label='Document', chunk\_node\_label='Chunk', chunk\_to\_document\_relationship\_type='FROM\_DOCUMENT', next\_chunk\_relationship\_type='NEXT\_CHUNK', node\_to\_chunk\_relationship\_type='FROM\_CHUNK', chunk\_id\_property='id', chunk\_index\_property='index', chunk\_text\_property='text', chunk\_embedding\_property='embedding')_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/kg_writer.html#Neo4jWriter.run)

Upserts a knowledge graph into a Neo4j database.

Parameters:

* **graph** ([_Neo4jGraph_](about:blank/types.html#neo4j_graphrag.experimental.components.types.Neo4jGraph "neo4j_graphrag.experimental.components.types.Neo4jGraph")) – The knowledge graph to upsert into the database.

* **lexical\_graph\_config** ([_LexicalGraphConfig_](about:blank/types.html#neo4j_graphrag.experimental.components.types.LexicalGraphConfig "neo4j_graphrag.experimental.components.types.LexicalGraphConfig")) – Node labels and relationship types for the lexical graph.

Return type:

[_KGWriterModel_](about:blank/types.html#neo4j_graphrag.experimental.components.kg_writer.KGWriterModel "neo4j_graphrag.experimental.components.kg_writer.KGWriterModel")

### SinglePropertyExactMatchResolver

_class_ neo4j\_graphrag.experimental.components.resolver.SinglePropertyExactMatchResolver(_driver_, _filter\_query\=None_, _resolve\_property\='name'_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/resolver.html#SinglePropertyExactMatchResolver)

Resolve entities with same label and exact same property (default is “name”).

Parameters:

* **driver** (_neo4j.Driver_) – The Neo4j driver to connect to the database.

* **filter\_query** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – To reduce the resolution scope, add a Cypher WHERE clause.

* **resolve\_property** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The property that will be compared (default: “name”). If values match exactly, entities are merged.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.experimental.components.resolver import SinglePropertyExactMatchResolver

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")
DATABASE = "neo4j"

driver = GraphDatabase.driver(URI, auth=AUTH)
resolver = SinglePropertyExactMatchResolver(driver=driver, neo4j_database=DATABASE)
await resolver.run()  # no expected parameters

```

_async_ run()
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/components/resolver.html#SinglePropertyExactMatchResolver.run)

Resolve entities based on the following rule: For each entity label, entities with the same ‘resolve\_property’ value (exact match) are grouped into a single node:

* Properties: the property from the first node will remain if already set, otherwise the first property in list will be written.

* Relationships: merge relationships with same type and target node.

See apoc.refactor.mergeNodes documentation for more details.

Return type:

_ResolutionStats_

Pipelines
-----------------------------------------------

### Pipeline

_class_ neo4j\_graphrag.experimental.pipeline.Pipeline(_store\=None_, _callback\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/pipeline.html#Pipeline)

This is the main pipeline, where components and their execution order are defined

Parameters:

* **store** (_Optional__\[**ResultStore**\]_)

* **callback** (_Optional__\[_[_EventCallbackProtocol_](about:blank/types.html#neo4j_graphrag.experimental.pipeline.types.EventCallbackProtocol "neo4j_graphrag.experimental.pipeline.types.EventCallbackProtocol")_\]_)

draw(_path_, _layout\='dot'_, _hide\_unused\_outputs\=True_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/pipeline.html#Pipeline.draw)

Parameters:

* **path** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **layout** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **hide\_unused\_outputs** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)"))

Return type:

[_Any_](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.13)")

add\_component(_component_, _name_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/pipeline.html#Pipeline.add_component)

Add a new component. Components are uniquely identified by their name. If ‘name’ is already in the pipeline, a ValueError is raised.

Parameters:

* **component** (_Component_)

* **name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

Return type:

None

connect(_start\_component\_name_, _end\_component\_name_, _input\_config\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/pipeline.html#Pipeline.connect)

Connect one component to another.

Parameters:

* **start\_component\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – name of the component as defined in the add\_component method

* **end\_component\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – name of the component as defined in the add\_component method

* **input\_config** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__\]_) – end component input configuration: propagate previous components outputs.

Raises:

[**PipelineDefinitionError**](#neo4j_graphrag.experimental.pipeline.exceptions.PipelineDefinitionError "neo4j_graphrag.experimental.pipeline.exceptions.PipelineDefinitionError") – if the provided component are not in the Pipeline or if the graph that would be created by this connection is cyclic.

Return type:

None

_async_ run(_data_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/pipeline.html#Pipeline.run)

Parameters:

**data** ([_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_Any_](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.13)")_\]_)

Return type:

_PipelineResult_

### SimpleKGPipeline

_class_ neo4j\_graphrag.experimental.pipeline.kg\_builder.SimpleKGPipeline(_llm_, _driver_, _embedder_, _entities=None_, _relations=None_, _potential\_schema=None_, _from\_pdf=True_, _text\_splitter=None_, _pdf\_loader=None_, _kg\_writer=None_, _on\_error='IGNORE'_, _prompt\_template=<neo4j\_graphrag.generation.prompts.ERExtractionTemplate object>_, _perform\_entity\_resolution=True_, _lexical\_graph\_config=None_, _neo4j\_database=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/kg_builder.html#SimpleKGPipeline)

A class to simplify the process of building a knowledge graph from text documents. It abstracts away the complexity of setting up the pipeline and its components.

Parameters:

* **llm** ([_LLMInterface_](#neo4j_graphrag.llm.LLMInterface "neo4j_graphrag.llm.LLMInterface")) – An instance of an LLM to use for entity and relation extraction.

* **driver** (_neo4j.Driver_) – A Neo4j driver instance for database connection.

* **embedder** ([_Embedder_](#neo4j_graphrag.embeddings.base.Embedder "neo4j_graphrag.embeddings.base.Embedder")) – An instance of an embedder used to generate chunk embeddings from text chunks.

* **entities** (_Optional__\[**List**\[**Union**\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__,_ [_SchemaEntity_](about:blank/types.html#neo4j_graphrag.experimental.components.schema.SchemaEntity "neo4j_graphrag.experimental.components.schema.SchemaEntity")_\]**\]**\]_) –

    A list of either:

  * str: entity labels

  * dict: following the SchemaEntity schema, ie with label, description and properties keys

* **relations** (_Optional__\[**List**\[**Union**\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__,_ [_SchemaRelation_](about:blank/types.html#neo4j_graphrag.experimental.components.schema.SchemaRelation "neo4j_graphrag.experimental.components.schema.SchemaRelation")_\]**\]**\]_) –

    A list of either:

  * str: relation label

  * dict: following the SchemaRelation schema, ie with label, description and properties keys

* **potential\_schema** (_Optional__\[**List**\[_[_tuple_](https://docs.python.org/3/library/stdtypes.html#tuple "(in Python v3.13)")_\]__\]_) – A list of potential schema relationships.

* **from\_pdf** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")) – Determines whether to include the PdfLoader in the pipeline. If True, expects file\_path input in run methods. If False, expects text input in run methods.

* **text\_splitter** (_Optional__\[_[_TextSplitter_](#neo4j_graphrag.experimental.components.text_splitters.base.TextSplitter "neo4j_graphrag.experimental.components.text_splitters.base.TextSplitter")_\]_) – A text splitter component. Defaults to FixedSizeSplitter().

* **pdf\_loader** (_Optional__\[_[_DataLoader_](#neo4j_graphrag.experimental.components.pdf_loader.DataLoader "neo4j_graphrag.experimental.components.pdf_loader.DataLoader")_\]_) – A PDF loader component. Defaults to PdfLoader().

* **kg\_writer** (_Optional__\[_[_KGWriter_](#neo4j_graphrag.experimental.components.kg_writer.KGWriter "neo4j_graphrag.experimental.components.kg_writer.KGWriter")_\]_) – A knowledge graph writer component. Defaults to Neo4jWriter().

* **on\_error** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Error handling strategy for the Entity and relation extractor. Defaults to “IGNORE”, where chunk will be ignored if extraction fails. Possible values: “RAISE” or “IGNORE”.

* **perform\_entity\_resolution** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")) – Merge entities with same label and name. Default: True

* **prompt\_template** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – A custom prompt template to use for extraction.

* **lexical\_graph\_config** (_Optional__\[_[_LexicalGraphConfig_](about:blank/types.html#neo4j_graphrag.experimental.components.types.LexicalGraphConfig "neo4j_graphrag.experimental.components.types.LexicalGraphConfig")_\]__,_ _optional_) – Lexical graph configuration to customize node labels and relationship types in the lexical graph.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

_async_ run\_async(_file\_path\=None_, _text\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/kg_builder.html#SimpleKGPipeline.run_async)

Asynchronously runs the knowledge graph building process.

Parameters:

* **file\_path** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – The path to the PDF file to process. Required if from\_pdf is True.

* **text** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – The text content to process. Required if from\_pdf is False.

Returns:

The result of the pipeline execution.

Return type:

PipelineResult

Config files
-----------------------------------------------------

### SimpleKGPipelineConfig

_class_ neo4j\_graphrag.experimental.pipeline.config.template\_pipeline.simple\_kg\_builder.SimpleKGPipelineConfig(_\*_, _neo4j\_config={}_, _llm\_config={}_, _embedder\_config={}_, _extras={}_, _template\_=PipelineType.SIMPLE\_KG\_PIPELINE_, _from\_pdf=False_, _entities=\[\]_, _relations=\[\]_, _potential\_schema=None_, _enforce\_schema=SchemaEnforcementMode.NONE_, _on\_error=OnError.IGNORE_, _prompt\_template=<neo4j\_graphrag.generation.prompts.ERExtractionTemplate object>_, _perform\_entity\_resolution=True_, _lexical\_graph\_config=None_, _neo4j\_database=None_, _pdf\_loader=None_, _kg\_writer=None_, _text\_splitter=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/config/template_pipeline/simple_kg_builder.html#SimpleKGPipelineConfig)

Parameters:

* **neo4j\_config** ([_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_Neo4jDriverType_](about:blank/types.html#neo4j_graphrag.experimental.pipeline.config.object_config.Neo4jDriverType "neo4j_graphrag.experimental.pipeline.config.object_config.Neo4jDriverType")_\]_)

* **llm\_config** ([_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_LLMType_](about:blank/types.html#neo4j_graphrag.experimental.pipeline.config.object_config.LLMType "neo4j_graphrag.experimental.pipeline.config.object_config.LLMType")_\]_)

* **embedder\_config** ([_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_EmbedderType_](about:blank/types.html#neo4j_graphrag.experimental.pipeline.config.object_config.EmbedderType "neo4j_graphrag.experimental.pipeline.config.object_config.EmbedderType")_\]_)

* **extras** ([_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)") _|_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)") _|_ [_ParamFromEnvConfig_](about:blank/types.html#neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig "neo4j_graphrag.experimental.pipeline.config.param_resolver.ParamFromEnvConfig") _|_ _ParamFromKeyConfig_ _|_ [_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_Any_](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.13)")_\]__\]_)

* **template\_** ([_Literal_](https://docs.python.org/3/library/typing.html#typing.Literal "(in Python v3.13)")_\[**PipelineType.SIMPLE\_KG\_PIPELINE**\]_)

* **from\_pdf** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)"))

* **entities** ([_Sequence_](https://docs.python.org/3/library/typing.html#typing.Sequence "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)") _|_ [_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)") _|_ [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]**\]**\]__\]_)

* **relations** ([_Sequence_](https://docs.python.org/3/library/typing.html#typing.Sequence "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)") _|_ [_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)") _|_ [_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]**\]**\]__\]_)

* **potential\_schema** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_tuple_](https://docs.python.org/3/library/stdtypes.html#tuple "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__\]_ _|_ _None_)

* **enforce\_schema** (_SchemaEnforcementMode_)

* **on\_error** (_OnError_)

* **prompt\_template** ([_ERExtractionTemplate_](#neo4j_graphrag.generation.prompts.ERExtractionTemplate "neo4j_graphrag.generation.prompts.ERExtractionTemplate") _|_ [_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **perform\_entity\_resolution** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)"))

* **lexical\_graph\_config** ([_LexicalGraphConfig_](about:blank/types.html#neo4j_graphrag.experimental.components.types.LexicalGraphConfig "neo4j_graphrag.experimental.components.types.LexicalGraphConfig") _|_ _None_)

* **neo4j\_database** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)") _|_ _None_)

* **pdf\_loader** ([_ComponentType_](about:blank/types.html#neo4j_graphrag.experimental.pipeline.config.object_config.ComponentType "neo4j_graphrag.experimental.pipeline.config.object_config.ComponentType") _|_ _None_)

* **kg\_writer** ([_ComponentType_](about:blank/types.html#neo4j_graphrag.experimental.pipeline.config.object_config.ComponentType "neo4j_graphrag.experimental.pipeline.config.object_config.ComponentType") _|_ _None_)

* **text\_splitter** ([_ComponentType_](about:blank/types.html#neo4j_graphrag.experimental.pipeline.config.object_config.ComponentType "neo4j_graphrag.experimental.pipeline.config.object_config.ComponentType") _|_ _None_)

### PipelineRunner

_class_ neo4j\_graphrag.experimental.pipeline.config.runner.PipelineRunner(_pipeline\_definition_, _config\=None_, _do\_cleaning\=False_)
[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/config/runner.html#PipelineRunner)

Pipeline runner builds a pipeline from different objects and exposes a run method to run pipeline

Pipeline can be built from: - A PipelineDefinition (\_\_init\_\_ method) - A PipelineConfig (from\_config method) - A config file (from\_config\_file method)

Parameters:

* **pipeline\_definition** (_PipelineDefinition_)

* **config** (_AbstractPipelineConfig_ _|_ _None_)

* **do\_cleaning** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)"))

Retrievers
-------------------------------------------------

### RetrieverInterface

_class_ neo4j\_graphrag.retrievers.base.Retriever(_driver_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/base.html#Retriever)

Abstract class for Neo4j retrievers

Parameters:

* **driver** (_neo4j.Driver_)

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

index\_name_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_

VERIFY\_NEO4J\_VERSION _\= True_

search(_\*args_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/base.html#Retriever.search)

Search method. Call the get\_search\_results method that returns a list of neo4j.Record, and format them using the function returned by get\_result\_formatter to return RetrieverResult.

Parameters:

* **args** ([_Any_](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.13)"))

* **kwargs** ([_Any_](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.13)"))

Return type:

[_RetrieverResult_](about:blank/types.html#neo4j_graphrag.types.RetrieverResult "neo4j_graphrag.types.RetrieverResult")

_abstract_ get\_search\_results(_\*args_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/base.html#Retriever.get_search_results)

This method must be implemented in each child class. It will receive the same parameters provided to the public interface via the search method, after validation. It returns a RawSearchResult object which comprises a list of neo4j.Record objects and an optional metadata dictionary that can contain retriever-level information.

Note that, even though this method is not intended to be called from outside the class, we make it public to make it clearer for the developers that it should be implemented in child classes.

Returns:

List of Neo4j Records and optional metadata dict

Return type:

[RawSearchResult](about:blank/types.html#neo4j_graphrag.types.RawSearchResult "neo4j_graphrag.types.RawSearchResult")

Parameters:

* **args** ([_Any_](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.13)"))

* **kwargs** ([_Any_](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.13)"))

get\_result\_formatter()
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/base.html#Retriever.get_result_formatter)

Returns the function to use to transform a neo4j.Record to a RetrieverResultItem.

Return type:

[_Callable_](https://docs.python.org/3/library/typing.html#typing.Callable "(in Python v3.13)")\[\[_Record_\], [_RetrieverResultItem_](about:blank/types.html#neo4j_graphrag.types.RetrieverResultItem "neo4j_graphrag.types.RetrieverResultItem")\]

default\_record\_formatter(_record_)
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/base.html#Retriever.default_record_formatter)

Best effort to guess the node-to-text method. Inherited classes can override this method to implement custom text formatting.

Parameters:

**record** (_Record_)

Return type:

[_RetrieverResultItem_](about:blank/types.html#neo4j_graphrag.types.RetrieverResultItem "neo4j_graphrag.types.RetrieverResultItem")

### VectorRetriever

_class_ neo4j\_graphrag.retrievers.VectorRetriever(_driver_, _index\_name_, _embedder\=None_, _return\_properties\=None_, _result\_formatter\=None_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/vector.html#VectorRetriever)

Provides retrieval method using vector search over embeddings. If an embedder is provided, it needs to have the required Embedder type.

Example:

```
import neo4j
from neo4j_graphrag.retrievers import VectorRetriever

driver = neo4j.GraphDatabase.driver(URI, auth=AUTH)

retriever = VectorRetriever(driver, "vector-index-name", custom_embedder)
retriever.search(query_text="Find me a book about Fremen", top_k=5)

```

or if the vector embedding of the query text is available:

```
retriever.search(query_vector=..., top_k=5)

```

Parameters:

* **driver** (_neo4j.Driver_) – The Neo4j Python driver.

* **index\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Vector index name.

* **embedder** (_Optional__\[_[_Embedder_](#neo4j_graphrag.embeddings.base.Embedder "neo4j_graphrag.embeddings.base.Embedder")_\]_) – Embedder object to embed query text.

* **return\_properties** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__\]_) – List of node properties to return.

* **result\_formatter** (_Optional__\[**Callable**\[**\[**neo4j.Record**\]**,_ [_RetrieverResultItem_](about:blank/types.html#neo4j_graphrag.types.RetrieverResultItem "neo4j_graphrag.types.RetrieverResultItem")_\]__\]_) –

    Provided custom function to transform a neo4j.Record to a RetrieverResultItem.

    Two variables are provided in the neo4j.Record:

  * node: Represents the node retrieved from the vector index search.

  * score: Denotes the similarity score.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Raises:

[**RetrieverInitializationError**](#neo4j_graphrag.exceptions.RetrieverInitializationError "neo4j_graphrag.exceptions.RetrieverInitializationError") – If validation of the input arguments fail.

search(_query\_vector\=None_, _query\_text\=None_, _top\_k\=5_, _effective\_search\_ratio\=1_, _filters\=None_)

Get the top\_k nearest neighbor embeddings for either provided query\_vector or query\_text. See the following documentation for more details:

* [Query a vector index](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/#indexes-vector-query)

* [db.index.vector.queryNodes()](https://neo4j.com/docs/operations-manual/5/reference/procedures/#procedure_db_index_vector_queryNodes)

To query by text, an embedder must be provided when the class is instantiated. The embedder is not required if query\_vector is passed.

Parameters:

* **query\_vector** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]__\]_) – The vector embeddings to get the closest neighbors of. Defaults to None.

* **query\_text** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – The text to get the closest neighbors of. Defaults to None.

* **top\_k** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – The number of neighbors to return. Defaults to 5.

* **effective\_search\_ratio** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – Controls the candidate pool size by multiplying top\_k to balance query accuracy and performance. Defaults to 1.

* **filters** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _Any__\]__\]_) – Filters for metadata pre-filtering. Defaults to None.

Raises:

* [**SearchValidationError**](#neo4j_graphrag.exceptions.SearchValidationError "neo4j_graphrag.exceptions.SearchValidationError") – If validation of the input arguments fail.

* [**EmbeddingRequiredError**](#neo4j_graphrag.exceptions.EmbeddingRequiredError "neo4j_graphrag.exceptions.EmbeddingRequiredError") – If no embedder is provided.

Returns:

The results of the search query as a list of neo4j.Record and an optional metadata dict

Return type:

[RawSearchResult](about:blank/types.html#neo4j_graphrag.types.RawSearchResult "neo4j_graphrag.types.RawSearchResult")

### VectorCypherRetriever

_class_ neo4j\_graphrag.retrievers.VectorCypherRetriever(_driver_, _index\_name_, _retrieval\_query_, _embedder\=None_, _result\_formatter\=None_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/vector.html#VectorCypherRetriever)

Provides retrieval method using vector similarity augmented by a Cypher query. This retriever builds on VectorRetriever. If an embedder is provided, it needs to have the required Embedder type.

Note: node is a variable from the base query that can be used in retrieval\_query as seen in the example below.

The retrieval\_query is additional Cypher that can allow for graph traversal after retrieving node.

Example:

```
import neo4j
from neo4j_graphrag.retrievers import VectorCypherRetriever

driver = neo4j.GraphDatabase.driver(URI, auth=AUTH)

retrieval_query = "MATCH (node)-[:AUTHORED_BY]->(author:Author)" "RETURN author.name"
retriever = VectorCypherRetriever(
  driver, "vector-index-name", retrieval_query, custom_embedder
)
retriever.search(query_text="Find me a book about Fremen", top_k=5)

```

Parameters:

* **driver** (_neo4j.Driver_) – The Neo4j Python driver.

* **index\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Vector index name.

* **retrieval\_query** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Cypher query that gets appended.

* **embedder** (_Optional__\[_[_Embedder_](#neo4j_graphrag.embeddings.base.Embedder "neo4j_graphrag.embeddings.base.Embedder")_\]_) – Embedder object to embed query text.

* **result\_formatter** (_Optional__\[**Callable**\[**\[**neo4j.Record**\]**,_ [_RetrieverResultItem_](about:blank/types.html#neo4j_graphrag.types.RetrieverResultItem "neo4j_graphrag.types.RetrieverResultItem")_\]__\]_) – Provided custom function to transform a neo4j.Record to a RetrieverResultItem.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Read more in the [User Guide](about:blank/user_guide_rag.html#vector-cypher-retriever-user-guide).

search(_query\_vector\=None_, _query\_text\=None_, _top\_k\=5_, _effective\_search\_ratio\=1_, _query\_params\=None_, _filters\=None_)

Get the top\_k nearest neighbor embeddings for either provided query\_vector or query\_text. See the following documentation for more details:

* [Query a vector index](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/#indexes-vector-query)

* [db.index.vector.queryNodes()](https://neo4j.com/docs/operations-manual/5/reference/procedures/#procedure_db_index_vector_queryNodes)

To query by text, an embedder must be provided when the class is instantiated. The embedder is not required if query\_vector is passed.

Parameters:

* **query\_vector** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]__\]_) – The vector embeddings to get the closest neighbors of. Defaults to None.

* **query\_text** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – The text to get the closest neighbors of. Defaults to None.

* **top\_k** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – The number of neighbors to return. Defaults to 5.

* **effective\_search\_ratio** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – Controls the candidate pool size by multiplying top\_k to balance query accuracy and performance. Defaults to 1.

* **query\_params** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _Any__\]__\]_) – Parameters for the Cypher query. Defaults to None.

* **filters** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _Any__\]__\]_) – Filters for metadata pre-filtering. Defaults to None.

Raises:

* [**SearchValidationError**](#neo4j_graphrag.exceptions.SearchValidationError "neo4j_graphrag.exceptions.SearchValidationError") – If validation of the input arguments fail.

* [**EmbeddingRequiredError**](#neo4j_graphrag.exceptions.EmbeddingRequiredError "neo4j_graphrag.exceptions.EmbeddingRequiredError") – If no embedder is provided.

Returns:

The results of the search query as a list of neo4j.Record and an optional metadata dict

Return type:

[RawSearchResult](about:blank/types.html#neo4j_graphrag.types.RawSearchResult "neo4j_graphrag.types.RawSearchResult")

### HybridRetriever

_class_ neo4j\_graphrag.retrievers.HybridRetriever(_driver_, _vector\_index\_name_, _fulltext\_index\_name_, _embedder\=None_, _return\_properties\=None_, _result\_formatter\=None_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/hybrid.html#HybridRetriever)

Provides retrieval method using combination of vector search over embeddings and fulltext search. If an embedder is provided, it needs to have the required Embedder type.

Example:

```
import neo4j
from neo4j_graphrag.retrievers import HybridRetriever

driver = neo4j.GraphDatabase.driver(URI, auth=AUTH)

retriever = HybridRetriever(
    driver, "vector-index-name", "fulltext-index-name", custom_embedder
)
retriever.search(query_text="Find me a book about Fremen", top_k=5)

```

Parameters:

* **driver** (_neo4j.Driver_) – The Neo4j Python driver.

* **vector\_index\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Vector index name.

* **fulltext\_index\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Fulltext index name.

* **embedder** (_Optional__\[_[_Embedder_](#neo4j_graphrag.embeddings.base.Embedder "neo4j_graphrag.embeddings.base.Embedder")_\]_) – Embedder object to embed query text.

* **return\_properties** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__\]_) – List of node properties to return.

* **result\_formatter** (_Optional__\[**Callable**\[**\[**neo4j.Record**\]**,_ [_RetrieverResultItem_](about:blank/types.html#neo4j_graphrag.types.RetrieverResultItem "neo4j_graphrag.types.RetrieverResultItem")_\]__\]_) – Provided custom function to transform a neo4j.Record to a RetrieverResultItem.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

    Two variables are provided in the neo4j.Record:

  * node: Represents the node retrieved from the vector index search.

  * score: Denotes the similarity score.

search(_query\_text_, _query\_vector\=None_, _top\_k\=5_, _effective\_search\_ratio\=1_, _ranker\=HybridSearchRanker.NAIVE_, _alpha\=None_)

Get the top\_k nearest neighbor embeddings for either provided query\_vector or query\_text. Both query\_vector and query\_text can be provided. If query\_vector is provided, then it will be preferred over the embedded query\_text for the vector search.

See the following documentation for more details:

* [Query a vector index](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/#indexes-vector-query)

* [db.index.vector.queryNodes()](https://neo4j.com/docs/operations-manual/5/reference/procedures/#procedure_db_index_vector_queryNodes)

* [db.index.fulltext.queryNodes()](https://neo4j.com/docs/operations-manual/5/reference/procedures/#procedure_db_index_fulltext_querynodes)

To query by text, an embedder must be provided when the class is instantiated.

Parameters:

* **query\_text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to get the closest neighbors of.

* **query\_vector** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]**\]**,_ _optional_) – The vector embeddings to get the closest neighbors of. Defaults to None.

* **top\_k** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")_,_ _optional_) – The number of neighbors to return. Defaults to 5.

* **effective\_search\_ratio** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – Controls the candidate pool size for the vector index by multiplying top\_k to balance query accuracy and performance. Defaults to 1.

* **ranker** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _HybridSearchRanker_) – Type of ranker to order the results from retrieval.

* **alpha** (_Optional__\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]_) – Weight for the vector score when using the linear ranker. The fulltext index score is multiplied by (1 - alpha). **Required** when using the linear ranker; must be between 0 and 1.

Raises:

* [**SearchValidationError**](#neo4j_graphrag.exceptions.SearchValidationError "neo4j_graphrag.exceptions.SearchValidationError") – If validation of the input arguments fail.

* [**EmbeddingRequiredError**](#neo4j_graphrag.exceptions.EmbeddingRequiredError "neo4j_graphrag.exceptions.EmbeddingRequiredError") – If no embedder is provided.

Returns:

The results of the search query as a list of neo4j.Record and an optional metadata dict

Return type:

[RawSearchResult](about:blank/types.html#neo4j_graphrag.types.RawSearchResult "neo4j_graphrag.types.RawSearchResult")

### HybridCypherRetriever

_class_ neo4j\_graphrag.retrievers.HybridCypherRetriever(_driver_, _vector\_index\_name_, _fulltext\_index\_name_, _retrieval\_query_, _embedder\=None_, _result\_formatter\=None_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/hybrid.html#HybridCypherRetriever)

Provides retrieval method using combination of vector search over embeddings and fulltext search, augmented by a Cypher query. This retriever builds on HybridRetriever. If an embedder is provided, it needs to have the required Embedder type.

Note: node is a variable from the base query that can be used in retrieval\_query as seen in the example below.

Example:

```
import neo4j
from neo4j_graphrag.retrievers import HybridCypherRetriever

driver = neo4j.GraphDatabase.driver(URI, auth=AUTH)

retrieval_query = "MATCH (node)-[:AUTHORED_BY]->(author:Author)" "RETURN author.name"
retriever = HybridCypherRetriever(
    driver, "vector-index-name", "fulltext-index-name", retrieval_query, custom_embedder
)
retriever.search(query_text="Find me a book about Fremen", top_k=5)

```

To query by text, an embedder must be provided when the class is instantiated.

Parameters:

* **driver** (_neo4j.Driver_) – The Neo4j Python driver.

* **vector\_index\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Vector index name.

* **fulltext\_index\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Fulltext index name.

* **retrieval\_query** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Cypher query that gets appended.

* **embedder** (_Optional__\[_[_Embedder_](#neo4j_graphrag.embeddings.base.Embedder "neo4j_graphrag.embeddings.base.Embedder")_\]_) – Embedder object to embed query text.

* **result\_formatter** (_Optional__\[**Callable**\[**\[**neo4j.Record**\]**,_ [_RetrieverResultItem_](about:blank/types.html#neo4j_graphrag.types.RetrieverResultItem "neo4j_graphrag.types.RetrieverResultItem")_\]__\]_) – Provided custom function to transform a neo4j.Record to a RetrieverResultItem.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Raises:

[**RetrieverInitializationError**](#neo4j_graphrag.exceptions.RetrieverInitializationError "neo4j_graphrag.exceptions.RetrieverInitializationError") – If validation of the input arguments fail.

search(_query\_text_, _query\_vector\=None_, _top\_k\=5_, _effective\_search\_ratio\=1_, _query\_params\=None_, _ranker\=HybridSearchRanker.NAIVE_, _alpha\=None_)

Get the top\_k nearest neighbor embeddings for either provided query\_vector or query\_text. Both query\_vector and query\_text can be provided. If query\_vector is provided, then it will be preferred over the embedded query\_text for the vector search.

See the following documentation for more details:

* [Query a vector index](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/#indexes-vector-query)

* [db.index.vector.queryNodes()](https://neo4j.com/docs/operations-manual/5/reference/procedures/#procedure_db_index_vector_queryNodes)

* [db.index.fulltext.queryNodes()](https://neo4j.com/docs/operations-manual/5/reference/procedures/#procedure_db_index_fulltext_querynodes)

Parameters:

* **query\_text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to get the closest neighbors of.

* **query\_vector** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]__\]_) – The vector embeddings to get the closest neighbors of. Defaults to None.

* **top\_k** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – The number of neighbors to return. Defaults to 5.

* **effective\_search\_ratio** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – Controls the candidate pool size for the vector index by multiplying top\_k to balance query accuracy and performance. Defaults to 1.

* **query\_params** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _Any__\]__\]_) – Parameters for the Cypher query. Defaults to None.

* **ranker** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _HybridSearchRanker_) – Type of ranker to order the results from retrieval.

* **alpha** (_Optional__\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]_) – Weight for the vector score when using the linear ranker. The fulltext index score is multiplied by (1 - alpha). **Required** when using the linear ranker; must be between 0 and 1.

Raises:

* [**SearchValidationError**](#neo4j_graphrag.exceptions.SearchValidationError "neo4j_graphrag.exceptions.SearchValidationError") – If validation of the input arguments fail.

* [**EmbeddingRequiredError**](#neo4j_graphrag.exceptions.EmbeddingRequiredError "neo4j_graphrag.exceptions.EmbeddingRequiredError") – If no embedder is provided.

Returns:

The results of the search query as a list of neo4j.Record and an optional metadata dict

Return type:

[RawSearchResult](about:blank/types.html#neo4j_graphrag.types.RawSearchResult "neo4j_graphrag.types.RawSearchResult")

### Text2CypherRetriever

_class_ neo4j\_graphrag.retrievers.Text2CypherRetriever(_driver_, _llm_, _neo4j\_schema\=None_, _examples\=None_, _result\_formatter\=None_, _custom\_prompt\=None_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/text2cypher.html#Text2CypherRetriever)

Allows for the retrieval of records from a Neo4j database using natural language. Converts a user’s natural language query to a Cypher query using an LLM, then retrieves records from a Neo4j database using the generated Cypher query.

Parameters:

* **driver** (_neo4j.Driver_) – The Neo4j Python driver.

* **llm** (_neo4j\_graphrag.generation.llm.LLMInterface_) – LLM object to generate the Cypher query.

* **neo4j\_schema** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – Neo4j schema used to generate the Cypher query.

* **examples** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__,_ _optional_) – Optional user input/query pairs for the LLM to use as examples.

* **custom\_prompt** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – Optional custom prompt to use instead of auto generated prompt. Will include the neo4j\_schema for schema and examples for examples prompt parameters, if they are provided.

* **result\_formatter** (_Optional__\[**Callable**\[**\[**neo4j.Record**\]**,_ [_RetrieverResultItem_](about:blank/types.html#neo4j_graphrag.types.RetrieverResultItem "neo4j_graphrag.types.RetrieverResultItem")_\]__\]_)

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

Raises:

[**RetrieverInitializationError**](#neo4j_graphrag.exceptions.RetrieverInitializationError "neo4j_graphrag.exceptions.RetrieverInitializationError") – If validation of the input arguments fail.

search(_query\_text_, _prompt\_params\=None_)

Converts query\_text to a Cypher query using an LLM.

Retrieve records from a Neo4j database using the generated Cypher query.

Parameters:

* **query\_text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The natural language query used to search the Neo4j database.

* **prompt\_params** (_Dict__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _Any__\]_) – additional values to inject into the custom prompt, if it is provided. If the schema or examples parameter is specified, it will overwrite the corresponding value passed during initialization. Example: {‘schema’: ‘this is the graph schema’}

Raises:

* [**SearchValidationError**](#neo4j_graphrag.exceptions.SearchValidationError "neo4j_graphrag.exceptions.SearchValidationError") – If validation of the input arguments fail.

* [**Text2CypherRetrievalError**](#neo4j_graphrag.exceptions.Text2CypherRetrievalError "neo4j_graphrag.exceptions.Text2CypherRetrievalError") – If the LLM fails to generate a correct Cypher query.

Returns:

The results of the search query as a list of neo4j.Record and an optional metadata dict

Return type:

[RawSearchResult](about:blank/types.html#neo4j_graphrag.types.RawSearchResult "neo4j_graphrag.types.RawSearchResult")

External Retrievers
-------------------------------------------------------------------

This section includes retrievers that integrate with databases external to Neo4j.

### WeaviateNeo4jRetriever

_class_ neo4j\_graphrag.retrievers.external.weaviate.weaviate.WeaviateNeo4jRetriever(_driver_, _client_, _collection_, _id\_property\_external_, _id\_property\_neo4j_, _embedder\=None_, _return\_properties\=None_, _retrieval\_query\=None_, _result\_formatter\=None_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/external/weaviate/weaviate.html#WeaviateNeo4jRetriever)

Provides retrieval method using vector search over embeddings with a Weaviate database. If an embedder is provided, it needs to have the required Embedder type.

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.retrievers import WeaviateNeo4jRetriever
from weaviate.connect.helpers import connect_to_local

with GraphDatabase.driver(NEO4J_URL, auth=NEO4J_AUTH) as neo4j_driver:
    with connect_to_local() as w_client:
        retriever = WeaviateNeo4jRetriever(
            driver=neo4j_driver,
            client=w_client,
            collection="Jeopardy",
            id_property_external="neo4j_id",
            id_property_neo4j="id"
        )

        result = retriever.search(query_text="biology", top_k=2)

```

Parameters:

* **driver** (_neo4j.Driver_) – The Neo4j Python driver.

* **client** (_WeaviateClient_) – The Weaviate client object.

* **collection** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Name of a set of Weaviate objects that share the same data structure.

* **id\_property\_external** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the Weaviate property that has the identifier that refers to a corresponding Neo4j node id property.

* **id\_property\_neo4j** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the Neo4j node property that’s used as the identifier for relating matches from Weaviate to Neo4j nodes.

* **embedder** (_Optional__\[_[_Embedder_](#neo4j_graphrag.embeddings.base.Embedder "neo4j_graphrag.embeddings.base.Embedder")_\]_) – Embedder object to embed query text.

* **return\_properties** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__\]_) – List of node properties to return.

* **result\_formatter** (_Optional__\[**Callable**\[**\[**neo4j.Record**\]**,_ [_RetrieverResultItem_](about:blank/types.html#neo4j_graphrag.types.RetrieverResultItem "neo4j_graphrag.types.RetrieverResultItem")_\]__\]_) – Function to transform a neo4j.Record to a RetrieverResultItem.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

* **retrieval\_query** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

Raises:

[**RetrieverInitializationError**](#neo4j_graphrag.exceptions.RetrieverInitializationError "neo4j_graphrag.exceptions.RetrieverInitializationError") – If validation of the input arguments fail.

search(_query\_vector\=None_, _query\_text\=None_, _top\_k\=5_, _\*\*kwargs_)

Get the top\_k nearest neighbor embeddings using Weaviate for either provided query\_vector or query\_text. Both query\_vector and query\_text can be provided. If query\_vector is provided, then it will be preferred over the embedded query\_text for the vector search. If query\_text is provided, then it will check if an embedder is provided and use it to generate the query\_vector. If no embedder is provided, then it will assume that the vectorizer is used in Weaviate.

Example:

```
import neo4j
from neo4j_graphrag.retrievers import WeaviateNeo4jRetriever

driver = neo4j.GraphDatabase.driver(URI, auth=AUTH)

retriever = WeaviateNeo4jRetriever(
    driver=driver,
    client=weaviate_client,
    collection="Jeopardy",
    id_property_external="neo4j_id",
    id_property_neo4j="id",
)

biology_embedding = ...
retriever.search(query_vector=biology_embedding, top_k=2)

```

Parameters:

* **query\_text** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – The text to get the closest neighbors of.

* **query\_vector** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]__\]_) – The vector embeddings to get the closest neighbors of. Defaults to None.

* **top\_k** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – The number of neighbors to return. Defaults to 5.

* **kwargs** (_Any_)

Raises:

[**SearchValidationError**](#neo4j_graphrag.exceptions.SearchValidationError "neo4j_graphrag.exceptions.SearchValidationError") – If validation of the input arguments fail.

Returns:

The results of the search query as a list of neo4j.Record and an optional metadata dict

Return type:

[RawSearchResult](about:blank/types.html#neo4j_graphrag.types.RawSearchResult "neo4j_graphrag.types.RawSearchResult")

### PineconeNeo4jRetriever

_class_ neo4j\_graphrag.retrievers.external.pinecone.pinecone.PineconeNeo4jRetriever(_driver_, _client_, _index\_name_, _id\_property\_neo4j_, _embedder\=None_, _return\_properties\=None_, _retrieval\_query\=None_, _result\_formatter\=None_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/external/pinecone/pinecone.html#PineconeNeo4jRetriever)

Provides retrieval method using vector search over embeddings with a Pinecone database. If an embedder is provided, it needs to have the required Embedder type.

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.retrievers import PineconeNeo4jRetriever
from pinecone import Pinecone

with GraphDatabase.driver(NEO4J_URL, auth=NEO4J_AUTH) as neo4j_driver:
    pc_client = Pinecone(PC_API_KEY)
    embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    retriever = PineconeNeo4jRetriever(
        driver=neo4j_driver,
        client=pc_client,
        index_name="jeopardy",
        id_property_neo4j="id",
        embedder=embedder,
    )

    result = retriever.search(query_text="biology", top_k=2)

```

Parameters:

* **driver** (_neo4j.Driver_) – The Neo4j Python driver.

* **client** (_Pinecone_) – The Pinecone client object.

* **index\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the Pinecone index.

* **id\_property\_neo4j** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the Neo4j node property that’s used as the identifier for relating matches from Pinecone to Neo4j nodes.

* **embedder** (_Optional__\[_[_Embedder_](#neo4j_graphrag.embeddings.base.Embedder "neo4j_graphrag.embeddings.base.Embedder")_\]_) – Embedder object to embed query text.

* **return\_properties** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__\]_) – List of node properties to return.

* **retrieval\_query** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Cypher query that gets appended.

* **result\_formatter** (_Optional__\[**Callable**\[**\[**neo4j.Record**\]**,_ [_RetrieverResultItem_](about:blank/types.html#neo4j_graphrag.types.RetrieverResultItem "neo4j_graphrag.types.RetrieverResultItem")_\]__\]_) – Function to transform a neo4j.Record to a RetrieverResultItem.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Raises:

[**RetrieverInitializationError**](#neo4j_graphrag.exceptions.RetrieverInitializationError "neo4j_graphrag.exceptions.RetrieverInitializationError") – If validation of the input arguments fail.

search(_query\_vector\=None_, _query\_text\=None_, _top\_k\=5_, _\*\*kwargs_)

Get the top\_k nearest neighbor embeddings using Pinecone for either provided query\_vector or query\_text. Both query\_vector and query\_text can be provided. If query\_vector is provided, then it will be preferred over the embedded query\_text for the vector search. If query\_text is provided, then it will check if an embedder is provided and use it to generate the query\_vector.

See the following documentation for more details: - [Query a vector index](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/#indexes-vector-query) - [db.index.vector.queryNodes()](https://neo4j.com/docs/operations-manual/5/reference/procedures/#procedure_db_index_vector_queryNodes) - [db.index.fulltext.queryNodes()](https://neo4j.com/docs/operations-manual/5/reference/procedures/#procedure_db_index_fulltext_querynodes)

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.retrievers import PineconeNeo4jRetriever
from pinecone import Pinecone

with GraphDatabase.driver(NEO4J_URL, auth=NEO4J_AUTH) as neo4j_driver:
    pc_client = Pinecone(PC_API_KEY)
    retriever = PineconeNeo4jRetriever(
        driver=neo4j_driver,
        client=pc_client,
        index_name="jeopardy",
        id_property_neo4j="id"
    )
    biology_embedding = ...
    retriever.search(query_vector=biology_embedding, top_k=2)

```

Parameters:

* **query\_text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to get the closest neighbors of.

* **query\_vector** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]**\]**,_ _optional_) – The vector embeddings to get the closest neighbors of. Defaults to None.

* **top\_k** (_Optional__\[_[_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")_\]_) – The number of neighbors to return. Defaults to 5.

* **kwargs** (_Any_)

Raises:

* [**SearchValidationError**](#neo4j_graphrag.exceptions.SearchValidationError "neo4j_graphrag.exceptions.SearchValidationError") – If validation of the input arguments fail.

* [**EmbeddingRequiredError**](#neo4j_graphrag.exceptions.EmbeddingRequiredError "neo4j_graphrag.exceptions.EmbeddingRequiredError") – If no embedder is provided when using text as an input.

Returns:

The results of the search query as a list of neo4j.Record and an optional metadata dict

Return type:

[RawSearchResult](about:blank/types.html#neo4j_graphrag.types.RawSearchResult "neo4j_graphrag.types.RawSearchResult")

### QdrantNeo4jRetriever

_class_ neo4j\_graphrag.retrievers.external.qdrant.qdrant.QdrantNeo4jRetriever(_driver_, _client_, _collection\_name_, _id\_property\_neo4j_, _id\_property\_external\='id'_, _embedder\=None_, _return\_properties\=None_, _retrieval\_query\=None_, _result\_formatter\=None_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/retrievers/external/qdrant/qdrant.html#QdrantNeo4jRetriever)

Provides retrieval method using vector search over embeddings with a Qdrant database.

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.retrievers import QdrantNeo4jRetriever
from qdrant_client import QdrantClient

with GraphDatabase.driver(NEO4J_URL, auth=NEO4J_AUTH) as neo4j_driver:
    client = QdrantClient()
    retriever = QdrantNeo4jRetriever(
        driver=neo4j_driver,
        client=client,
        collection_name="my_collection",
        id_property_external="neo4j_id"
    )
    embedding = ...
    retriever.search(query_vector=embedding, top_k=2)

```

Parameters:

* **driver** (_neo4j.Driver_) – The Neo4j Python driver.

* **client** (_QdrantClient_) – The Qdrant client object.

* **collection\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the Qdrant collection to use.

* **id\_property\_neo4j** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the Neo4j node property that’s used as the identifier for relating matches from Qdrant to Neo4j nodes.

* **id\_property\_external** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the Qdrant payload property with identifier that refers to a corresponding Neo4j node id property.

* **embedder** (_Optional__\[_[_Embedder_](#neo4j_graphrag.embeddings.base.Embedder "neo4j_graphrag.embeddings.base.Embedder")_\]_) – Embedder object to embed query text.

* **return\_properties** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__\]_) – List of node properties to return.

* **result\_formatter** (_Optional__\[**Callable**\[**\[**neo4j.Record**\]**,_ [_RetrieverResultItem_](about:blank/types.html#neo4j_graphrag.types.RetrieverResultItem "neo4j_graphrag.types.RetrieverResultItem")_\]__\]_) – Function to transform a neo4j.Record to a RetrieverResultItem.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

* **retrieval\_query** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

Raises:

[**RetrieverInitializationError**](#neo4j_graphrag.exceptions.RetrieverInitializationError "neo4j_graphrag.exceptions.RetrieverInitializationError") – If validation of the input arguments fail.

search(_query\_vector\=None_, _query\_text\=None_, _top\_k\=5_, _\*\*kwargs_)

Get the top\_k nearest neighbour embeddings using Qdrant for either provided query\_vector or query\_text. If query\_text is provided, then the provided embedder is used to generate the query\_vector.

See the following documentation for more details: - [Query a vector index](https://neo4j.com/docs/cypher-manual/current/indexes-for-vector-search/#indexes-vector-query) - [db.index.vector.queryNodes()](https://neo4j.com/docs/operations-manual/5/reference/procedures/#procedure_db_index_vector_queryNodes) - [db.index.fulltext.queryNodes()](https://neo4j.com/docs/operations-manual/5/reference/procedures/#procedure_db_index_fulltext_querynodes)

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.retrievers import QdrantNeo4jRetriever
from qdrant_client import QdrantClient

with GraphDatabase.driver(NEO4J_URL, auth=NEO4J_AUTH) as neo4j_driver:
    client = QdrantClient()
    retriever = QdrantNeo4jRetriever(
        driver=neo4j_driver,
        client=client,
        collection_name="my_collection",
        id_property_external="neo4j_id"
    )
    embedding = ...
    retriever.search(query_vector=embedding, top_k=2)

```

Parameters:

* **query\_text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to get the closest neighbours of.

* **query\_vector** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]**\]**,_ _optional_) – The vector embeddings to get the closest neighbours of. Defaults to None.

* **top\_k** (_Optional__\[_[_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")_\]_) – The number of neighbours to return. Defaults to 5.

* **kwargs** (_Any_) – Additional keyword arguments to pass to QdrantClient#query().

Raises:

* [**SearchValidationError**](#neo4j_graphrag.exceptions.SearchValidationError "neo4j_graphrag.exceptions.SearchValidationError") – If validation of the input arguments fail.

* [**EmbeddingRequiredError**](#neo4j_graphrag.exceptions.EmbeddingRequiredError "neo4j_graphrag.exceptions.EmbeddingRequiredError") – If no embedder is provided when using text as an input.

Returns:

The results of the search query as a list of neo4j.Record and an optional metadata dict

Return type:

[RawSearchResult](about:blank/types.html#neo4j_graphrag.types.RawSearchResult "neo4j_graphrag.types.RawSearchResult")

Embedder
---------------------------------------------

_class_ neo4j\_graphrag.embeddings.base.Embedder[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/base.html#Embedder)

Interface for embedding models. An embedder passed into a retriever must implement this interface.

_abstract_ embed\_query(_text_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/base.html#Embedder.embed_query)

Embed query text.

Parameters:

**text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Text to convert to vector embedding

Returns:

A vector embedding.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")\[[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")\]

### SentenceTransformerEmbeddings

_class_ neo4j\_graphrag.embeddings.sentence\_transformers.SentenceTransformerEmbeddings(_model\='all-MiniLM-L6-v2'_, _\*args_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/sentence_transformers.html#SentenceTransformerEmbeddings)

Parameters:

* **model** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **args** ([_Any_](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.13)"))

* **kwargs** ([_Any_](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.13)"))

embed\_query(_text_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/sentence_transformers.html#SentenceTransformerEmbeddings.embed_query)

Embed query text.

Parameters:

**text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Text to convert to vector embedding

Returns:

A vector embedding.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")\[[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")\]

### OpenAIEmbeddings

_class_ neo4j\_graphrag.embeddings.openai.OpenAIEmbeddings(_model\='text-embedding-ada-002'_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/openai.html#OpenAIEmbeddings)

OpenAI embeddings class. This class uses the OpenAI python client to generate embeddings for text data.

Parameters:

* **model** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the OpenAI embedding model to use. Defaults to “text-embedding-ada-002”.

* **kwargs** (_Any_) – All other parameters will be passed to the openai.OpenAI init.

### AzureOpenAIEmbeddings

_class_ neo4j\_graphrag.embeddings.openai.AzureOpenAIEmbeddings(_model\='text-embedding-ada-002'_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/openai.html#AzureOpenAIEmbeddings)

Azure OpenAI embeddings class. This class uses the Azure OpenAI python client to generate embeddings for text data.

Parameters:

* **model** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the Azure OpenAI embedding model to use. Defaults to “text-embedding-ada-002”.

* **kwargs** (_Any_) – All other parameters will be passed to the openai.AzureOpenAI init.

### OllamaEmbeddings

_class_ neo4j\_graphrag.embeddings.ollama.OllamaEmbeddings(_model_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/ollama.html#OllamaEmbeddings)

Ollama embeddings class. This class uses the ollama Python client to generate vector embeddings for text data.

Parameters:

* **model** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the Mistral AI text embedding model to use. Defaults to “mistral-embed”.

* **kwargs** (_Any_)

embed\_query(_text_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/ollama.html#OllamaEmbeddings.embed_query)

Generate embeddings for a given query using an Ollama text embedding model.

Parameters:

* **text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to generate an embedding for.

* **\*\*kwargs** (_Any_) – Additional keyword arguments to pass to the Ollama client.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")\[[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")\]

### VertexAIEmbeddings

_class_ neo4j\_graphrag.embeddings.vertexai.VertexAIEmbeddings(_model\='text-embedding-004'_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/vertexai.html#VertexAIEmbeddings)

Vertex AI embeddings class. This class uses the Vertex AI Python client to generate vector embeddings for text data.

Parameters:

**model** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the Vertex AI text embedding model to use. Defaults to “text-embedding-004”.

embed\_query(_text_, _task\_type\='RETRIEVAL\_QUERY'_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/vertexai.html#VertexAIEmbeddings.embed_query)

Generate embeddings for a given query using a Vertex AI text embedding model.

Parameters:

* **text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to generate an embedding for.

* **task\_type** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The type of the text embedding task. Defaults to “RETRIEVAL\_QUERY”. See [https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api#tasktype](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api#tasktype) for a full list.

* **\*\*kwargs** (_Any_) – Additional keyword arguments to pass to the Vertex AI client’s get\_embeddings method.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")\[[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")\]

### MistralAIEmbeddings

_class_ neo4j\_graphrag.embeddings.mistral.MistralAIEmbeddings(_model\='mistral-embed'_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/mistral.html#MistralAIEmbeddings)

Mistral AI embeddings class. This class uses the Mistral AI Python client to generate vector embeddings for text data.

Parameters:

* **model** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the Mistral AI text embedding model to use. Defaults to “mistral-embed”.

* **kwargs** (_Any_)

embed\_query(_text_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/mistral.html#MistralAIEmbeddings.embed_query)

Generate embeddings for a given query using a Mistral AI text embedding model.

Parameters:

* **text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to generate an embedding for.

* **\*\*kwargs** (_Any_) – Additional keyword arguments to pass to the Mistral AI client.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")\[[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")\]

### CohereEmbeddings

_class_ neo4j\_graphrag.embeddings.cohere.CohereEmbeddings(_model\=''_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/cohere.html#CohereEmbeddings)

Parameters:

* **model** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **kwargs** (_Any_)

embed\_query(_text_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/embeddings/cohere.html#CohereEmbeddings.embed_query)

Embed query text.

Parameters:

* **text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Text to convert to vector embedding

* **kwargs** ([_Any_](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.13)"))

Returns:

A vector embedding.

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")\[[float](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")\]

Generation
-------------------------------------------------

### LLM

#### LLMInterface

_class_ neo4j\_graphrag.llm.LLMInterface(_model\_name_, _model\_params\=None_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/base.html#LLMInterface)

Interface for large language models.

Parameters:

* **model\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the language model.

* **model\_params** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\]_) – Additional parameters passed to the model when text is sent to it. Defaults to None.

* **\*\*kwargs** (_Any_) – Arguments passed to the model when for the class is initialised. Defaults to None.

_abstract_ invoke(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/base.html#LLMInterface.invoke)

Sends a text input to the LLM and retrieves a response.

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Text sent to the LLM.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – An option to override the llm system message for this invocation.

Returns:

The response from the LLM.

Return type:

[LLMResponse](about:blank/types.html#neo4j_graphrag.llm.types.LLMResponse "neo4j_graphrag.llm.types.LLMResponse")

Raises:

[**LLMGenerationError**](#neo4j_graphrag.exceptions.LLMGenerationError "neo4j_graphrag.exceptions.LLMGenerationError") – If anything goes wrong.

_abstract async_ ainvoke(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/base.html#LLMInterface.ainvoke)

Asynchronously sends a text input to the LLM and retrieves a response.

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Text sent to the LLM.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – An option to override the llm system message for this invocation.

Returns:

The response from the LLM.

Return type:

[LLMResponse](about:blank/types.html#neo4j_graphrag.llm.types.LLMResponse "neo4j_graphrag.llm.types.LLMResponse")

Raises:

[**LLMGenerationError**](#neo4j_graphrag.exceptions.LLMGenerationError "neo4j_graphrag.exceptions.LLMGenerationError") – If anything goes wrong.

#### OpenAILLM

_class_ neo4j\_graphrag.llm.openai\_llm.OpenAILLM(_model\_name_, _model\_params\=None_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/openai_llm.html#OpenAILLM)

Parameters:

* **model\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **model\_params** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _Any__\]__\]_)

* **kwargs** (_Any_)

#### AzureOpenAILLM

_class_ neo4j\_graphrag.llm.openai\_llm.AzureOpenAILLM(_model\_name_, _model\_params\=None_, _system\_instruction\=None_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/openai_llm.html#AzureOpenAILLM)

Parameters:

* **model\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **model\_params** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _Any__\]__\]_)

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

* **kwargs** (_Any_)

#### OllamaLLM

_class_ neo4j\_graphrag.llm.ollama\_llm.OllamaLLM(_model\_name_, _model\_params\=None_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/ollama_llm.html#OllamaLLM)

Parameters:

* **model\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **model\_params** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _Any__\]__\]_)

* **kwargs** (_Any_)

get\_messages(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/ollama_llm.html#OllamaLLM.get_messages)

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_)

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

Return type:

Sequence\[Message\]

invoke(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/ollama_llm.html#OllamaLLM.invoke)

Sends text to the LLM and returns a response.

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to send to the LLM.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – An option to override the llm system message for this invocation.

Returns:

The response from the LLM.

Return type:

[LLMResponse](about:blank/types.html#neo4j_graphrag.llm.types.LLMResponse "neo4j_graphrag.llm.types.LLMResponse")

_async_ ainvoke(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/ollama_llm.html#OllamaLLM.ainvoke)

Asynchronously sends a text input to the OpenAI chat completion model and returns the response’s content.

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Text sent to the LLM.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – An option to override the llm system message for this invocation.

Returns:

The response from OpenAI.

Return type:

[LLMResponse](about:blank/types.html#neo4j_graphrag.llm.types.LLMResponse "neo4j_graphrag.llm.types.LLMResponse")

Raises:

[**LLMGenerationError**](#neo4j_graphrag.exceptions.LLMGenerationError "neo4j_graphrag.exceptions.LLMGenerationError") – If anything goes wrong.

#### VertexAILLM

_class_ neo4j\_graphrag.llm.vertexai\_llm.VertexAILLM(_model\_name\='gemini-1.5-flash-001'_, _model\_params\=None_, _system\_instruction\=None_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/vertexai_llm.html#VertexAILLM)

Interface for large language models on Vertex AI

Parameters:

* **model\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _optional_) – Name of the LLM to use. Defaults to “gemini-1.5-flash-001”.

* **model\_params** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\]__,_ _optional_) – Additional parameters passed to the model when text is sent to it. Defaults to None.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – Optional\[str\], optional): Additional instructions for setting the behavior and context for the model in a conversation. Defaults to None.

* **\*\*kwargs** (_Any_) – Arguments passed to the model when for the class is initialised. Defaults to None.

Raises:

[**LLMGenerationError**](#neo4j_graphrag.exceptions.LLMGenerationError "neo4j_graphrag.exceptions.LLMGenerationError") – If there’s an error generating the response from the model.

Example:

```
from neo4j_graphrag.llm import VertexAILLM
from vertexai.generative_models import GenerationConfig

generation_config = GenerationConfig(temperature=0.0)
llm = VertexAILLM(
    model_name="gemini-1.5-flash-001", generation_config=generation_config
)
llm.invoke("Who is the mother of Paul Atreides?")

```

get\_messages(_input_, _message\_history\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/vertexai_llm.html#VertexAILLM.get_messages)

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **message\_history** ([_List_](https://docs.python.org/3/library/typing.html#typing.List "(in Python v3.13)")_\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]_ _|_ _MessageHistory_ _|_ _None_)

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")\[_Content_\]

invoke(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/vertexai_llm.html#VertexAILLM.invoke)

Sends text to the LLM and returns a response.

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to send to the LLM.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – An option to override the llm system message for this invocation.

Returns:

The response from the LLM.

Return type:

[LLMResponse](about:blank/types.html#neo4j_graphrag.llm.types.LLMResponse "neo4j_graphrag.llm.types.LLMResponse")

_async_ ainvoke(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/vertexai_llm.html#VertexAILLM.ainvoke)

Asynchronously sends text to the LLM and returns a response.

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to send to the LLM.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – An option to override the llm system message for this invocation.

Returns:

The response from the LLM.

Return type:

[LLMResponse](about:blank/types.html#neo4j_graphrag.llm.types.LLMResponse "neo4j_graphrag.llm.types.LLMResponse")

#### AnthropicLLM

_class_ neo4j\_graphrag.llm.anthropic\_llm.AnthropicLLM(_model\_name_, _model\_params\=None_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/anthropic_llm.html#AnthropicLLM)

Interface for large language models on Anthropic

Parameters:

* **model\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _optional_) – Name of the LLM to use. Defaults to “gemini-1.5-flash-001”.

* **model\_params** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\]__,_ _optional_) – Additional parameters passed to the model when text is sent to it. Defaults to None.

* **system\_instruction** – Optional\[str\], optional): Additional instructions for setting the behavior and context for the model in a conversation. Defaults to None.

* **\*\*kwargs** (_Any_) – Arguments passed to the model when for the class is initialised. Defaults to None.

Raises:

[**LLMGenerationError**](#neo4j_graphrag.exceptions.LLMGenerationError "neo4j_graphrag.exceptions.LLMGenerationError") – If there’s an error generating the response from the model.

Example:

```
from neo4j_graphrag.llm import AnthropicLLM

llm = AnthropicLLM(
    model_name="claude-3-opus-20240229",
    model_params={"max_tokens": 1000},
    api_key="sk...",   # can also be read from env vars
)
llm.invoke("Who is the mother of Paul Atreides?")

```

get\_messages(_input_, _message\_history\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/anthropic_llm.html#AnthropicLLM.get_messages)

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_)

Return type:

Iterable\[MessageParam\]

invoke(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/anthropic_llm.html#AnthropicLLM.invoke)

Sends text to the LLM and returns a response.

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to send to the LLM.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – An option to override the llm system message for this invocation.

Returns:

The response from the LLM.

Return type:

[LLMResponse](about:blank/types.html#neo4j_graphrag.llm.types.LLMResponse "neo4j_graphrag.llm.types.LLMResponse")

_async_ ainvoke(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/anthropic_llm.html#AnthropicLLM.ainvoke)

Asynchronously sends text to the LLM and returns a response.

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to send to the LLM.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – An option to override the llm system message for this invocation.

Returns:

The response from the LLM.

Return type:

[LLMResponse](about:blank/types.html#neo4j_graphrag.llm.types.LLMResponse "neo4j_graphrag.llm.types.LLMResponse")

#### CohereLLM

_class_ neo4j\_graphrag.llm.cohere\_llm.CohereLLM(_model\_name\=''_, _model\_params\=None_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/cohere_llm.html#CohereLLM)

Interface for large language models on the Cohere platform

Parameters:

* **model\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _optional_) – Name of the LLM to use. Defaults to “gemini-1.5-flash-001”.

* **model\_params** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\]__,_ _optional_) – Additional parameters passed to the model when text is sent to it. Defaults to None.

* **system\_instruction** – Optional\[str\], optional): Additional instructions for setting the behavior and context for the model in a conversation. Defaults to None.

* **\*\*kwargs** (_Any_) – Arguments passed to the model when for the class is initialised. Defaults to None.

Raises:

[**LLMGenerationError**](#neo4j_graphrag.exceptions.LLMGenerationError "neo4j_graphrag.exceptions.LLMGenerationError") – If there’s an error generating the response from the model.

Example:

```
from neo4j_graphrag.llm import CohereLLM

llm = CohereLLM(api_key="...")
llm.invoke("Say something")

```

get\_messages(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/cohere_llm.html#CohereLLM.get_messages)

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_)

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

Return type:

ChatMessages

invoke(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/cohere_llm.html#CohereLLM.invoke)

Sends text to the LLM and returns a response.

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to send to the LLM.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – An option to override the llm system message for this invocation.

Returns:

The response from the LLM.

Return type:

[LLMResponse](about:blank/types.html#neo4j_graphrag.llm.types.LLMResponse "neo4j_graphrag.llm.types.LLMResponse")

_async_ ainvoke(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/cohere_llm.html#CohereLLM.ainvoke)

Asynchronously sends text to the LLM and returns a response.

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The text to send to the LLM.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – An option to override the llm system message for this invocation.

Returns:

The response from the LLM.

Return type:

[LLMResponse](about:blank/types.html#neo4j_graphrag.llm.types.LLMResponse "neo4j_graphrag.llm.types.LLMResponse")

#### MistralAILLM

_class_ neo4j\_graphrag.llm.mistralai\_llm.MistralAILLM(_model\_name_, _model\_params\=None_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/mistralai_llm.html#MistralAILLM)

Parameters:

* **model\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **model\_params** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _Any__\]__\]_)

* **kwargs** (_Any_)

get\_messages(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/mistralai_llm.html#MistralAILLM.get_messages)

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **message\_history** ([_List_](https://docs.python.org/3/library/typing.html#typing.List "(in Python v3.13)")_\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]_ _|_ _MessageHistory_ _|_ _None_)

* **system\_instruction** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)") _|_ _None_)

Return type:

[list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")\[[_Annotated_](https://docs.python.org/3/library/typing.html#typing.Annotated "(in Python v3.13)")\[_Annotated_\[_AssistantMessage_, _Tag_(tag=assistant)\] | _Annotated_\[_SystemMessage_, _Tag_(tag=system)\] | _Annotated_\[_ToolMessage_, _Tag_(tag=tool)\] | _Annotated_\[_UserMessage_, _Tag_(tag=user)\], _Discriminator_(discriminator=~mistralai.models.chatcompletionrequest.<lambda>, custom\_error\_type=None, custom\_error\_message=None, custom\_error\_context=None)\]\]

invoke(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/mistralai_llm.html#MistralAILLM.invoke)

Sends a text input to the Mistral chat completion model and returns the response’s content.

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Text sent to the LLM.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – An option to override the llm system message for this invocation.

Returns:

The response from MistralAI.

Return type:

[LLMResponse](about:blank/types.html#neo4j_graphrag.llm.types.LLMResponse "neo4j_graphrag.llm.types.LLMResponse")

Raises:

[**LLMGenerationError**](#neo4j_graphrag.exceptions.LLMGenerationError "neo4j_graphrag.exceptions.LLMGenerationError") – If anything goes wrong.

_async_ ainvoke(_input_, _message\_history\=None_, _system\_instruction\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/llm/mistralai_llm.html#MistralAILLM.ainvoke)

Asynchronously sends a text input to the MistralAI chat completion model and returns the response’s content.

Parameters:

* **input** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Text sent to the LLM.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **system\_instruction** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – An option to override the llm system message for this invocation.

Returns:

The response from MistralAI.

Return type:

[LLMResponse](about:blank/types.html#neo4j_graphrag.llm.types.LLMResponse "neo4j_graphrag.llm.types.LLMResponse")

Raises:

[**LLMGenerationError**](#neo4j_graphrag.exceptions.LLMGenerationError "neo4j_graphrag.exceptions.LLMGenerationError") – If anything goes wrong.

### PromptTemplate

_class_ neo4j\_graphrag.generation.prompts.PromptTemplate(_template\=None_, _expected\_inputs\=None_, _system\_instructions\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/generation/prompts.html#PromptTemplate)

This class is used to generate a parameterized prompt. It is defined from a string (the template) using the Python format syntax (parameters between curly braces {}) and a list of required inputs. Before sending the instructions to an LLM, call the format method that will replace parameters with the provided values. If any of the expected inputs is missing, a PromptMissingInputError is raised.

Parameters:

* **template** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

* **expected\_inputs** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__\]_)

* **system\_instructions** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

DEFAULT\_SYSTEM\_INSTRUCTIONS_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_ _\= ''_

DEFAULT\_TEMPLATE_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_ _\= ''_

EXPECTED\_INPUTS_: [list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")\]_ _\= \[\]_

format(_\*args_, _\*\*kwargs_)
[\[source\]](about:blank/_modules/neo4j_graphrag/generation/prompts.html#PromptTemplate.format)

This method is used to replace parameters with the provided values. Parameters must be provided: - as kwargs - as args if using the same order as in the expected inputs

Example:

```
prompt_template = PromptTemplate(
    template='''Explain the following concept to {target_audience}:
    Concept: {concept}
    Answer:
    ''',
    expected_inputs=['target_audience', 'concept']
)
prompt = prompt_template.format('12 yo children', concept='graph database')
print(prompt)

# Result:
# '''Explain the following concept to 12 yo children:
# Concept: graph database
# Answer:
# '''

```

Parameters:

* **args** ([_Any_](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.13)"))

* **kwargs** ([_Any_](https://docs.python.org/3/library/typing.html#typing.Any "(in Python v3.13)"))

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

#### RagTemplate

_class_ neo4j\_graphrag.generation.prompts.RagTemplate(_template\=None_, _expected\_inputs\=None_, _system\_instructions\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/generation/prompts.html#RagTemplate)

Parameters:

* **template** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

* **expected\_inputs** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__\]_)

* **system\_instructions** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

DEFAULT\_SYSTEM\_INSTRUCTIONS_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_ _\= 'Answer the user question using the provided context.'_

DEFAULT\_TEMPLATE_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_ _\= 'Context:\\n{context}\\n\\nExamples:\\n{examples}\\n\\nQuestion:\\n{query\_text}\\n\\nAnswer:\\n'_

EXPECTED\_INPUTS_: [list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")\]_ _\= \['context', 'query\_text', 'examples'\]_

#### Text2CypherTemplate

_class_ neo4j\_graphrag.generation.prompts.Text2CypherTemplate(_template\=None_, _expected\_inputs\=None_, _system\_instructions\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/generation/prompts.html#Text2CypherTemplate)

Parameters:

* **template** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

* **expected\_inputs** (_Optional__\[_[_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]__\]_)

* **system\_instructions** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_)

DEFAULT\_TEMPLATE_: [str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_ _\= '\\nTask: Generate a Cypher statement for querying a Neo4j graph database from a user input.\\n\\nSchema:\\n{schema}\\n\\nExamples (optional):\\n{examples}\\n\\nInput:\\n{query\_text}\\n\\nDo not use any properties or relationships not included in the schema.\\nDo not include triple backticks \`\`\` or any additional text except the generated Cypher statement in your response.\\n\\nCypher query:\\n'_

EXPECTED\_INPUTS_: [list](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")\]_ _\= \['query\_text'\]_

RAG
-----------------------------------

### GraphRAG

_class_ neo4j\_graphrag.generation.graphrag.GraphRAG(_retriever_, _llm_, _prompt\_template=<neo4j\_graphrag.generation.prompts.RagTemplate object>_)
[\[source\]](about:blank/_modules/neo4j_graphrag/generation/graphrag.html#GraphRAG)

Performs a GraphRAG search using a specific retriever and LLM.

Example:

```
import neo4j
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.llm.openai_llm import OpenAILLM
from neo4j_graphrag.generation import GraphRAG

driver = neo4j.GraphDatabase.driver(URI, auth=AUTH)

retriever = VectorRetriever(driver, "vector-index-name", custom_embedder)
llm = OpenAILLM()
graph_rag = GraphRAG(retriever, llm)
graph_rag.search(query_text="Find me a book about Fremen")

```

Parameters:

* **retriever** ([_Retriever_](#neo4j_graphrag.retrievers.base.Retriever "neo4j_graphrag.retrievers.base.Retriever")) – The retriever used to find relevant context to pass to the LLM.

* **llm** ([_LLMInterface_](#neo4j_graphrag.llm.LLMInterface "neo4j_graphrag.llm.LLMInterface")) – The LLM used to generate the answer.

* **prompt\_template** ([_RagTemplate_](#neo4j_graphrag.generation.prompts.RagTemplate "neo4j_graphrag.generation.prompts.RagTemplate")) – The prompt template that will be formatted with context and user question and passed to the LLM.

Raises:

[**RagInitializationError**](#neo4j_graphrag.exceptions.RagInitializationError "neo4j_graphrag.exceptions.RagInitializationError") – If validation of the input arguments fail.

search(_query\_text\=''_, _message\_history\=None_, _examples\=''_, _retriever\_config\=None_, _return\_context\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/generation/graphrag.html#GraphRAG.search)

Warning

The default value of ‘return\_context’ will change from ‘False’ to ‘True’ in a future version.

This method performs a full RAG search:

1. Retrieval: context retrieval

2. Augmentation: prompt formatting

3. Generation: answer generation with LLM

Parameters:

* **query\_text** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The user question.

* **message\_history** (_Optional__\[**Union**\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]**,_ _MessageHistory__\]**\]_) – A collection previous messages, with each message having a specific role assigned.

* **examples** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – Examples added to the LLM prompt.

* **retriever\_config** (_Optional__\[_[_dict_](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")_\]_) – Parameters passed to the retriever. search method; e.g.: top\_k

* **return\_context** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")) – Whether to append the retriever result to the final result (default: False).

Returns:

The LLM-generated answer.

Return type:

[RagResultModel](about:blank/types.html#neo4j_graphrag.generation.types.RagResultModel "neo4j_graphrag.generation.types.RagResultModel")

conversation\_prompt(_summary_, _current\_query_)
[\[source\]](about:blank/_modules/neo4j_graphrag/generation/graphrag.html#GraphRAG.conversation_prompt)

Parameters:

* **summary** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

* **current\_query** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"))

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Database Interaction
---------------------------------------------------------------------

neo4j\_graphrag.indexes.create\_vector\_index(_driver_, _name_, _label_, _embedding\_property_, _dimensions_, _similarity\_fn_, _fail\_if\_exists\=False_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/indexes.html#create_vector_index)

This method constructs a Cypher query and executes it to create a new vector index in Neo4j.

See Cypher manual on [creating vector indexes](https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/vector-indexes/#create-vector-index).

Ensure that the index name provided is unique within the database context.

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.indexes import create_vector_index

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

INDEX_NAME = "vector-index-name"

# Connect to Neo4j database
driver = GraphDatabase.driver(URI, auth=AUTH)

# Creating the index
create_vector_index(
    driver,
    INDEX_NAME,
    label="Document",
    embedding_property="vectorProperty",
    dimensions=1536,
    similarity_fn="euclidean",
    fail_if_exists=False,
)

```

Parameters:

* **driver** (_neo4j.Driver_) – Neo4j Python driver instance.

* **name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The unique name of the index.

* **label** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The node label to be indexed.

* **embedding\_property** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The property key of a node which contains embedding values.

* **dimensions** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – Vector embedding dimension

* **similarity\_fn** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – case-insensitive values for the vector similarity function: `euclidean` or `cosine`.

* **fail\_if\_exists** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")) – If True raise an error if the index already exists. Defaults to False.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Raises:

* [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError "(in Python v3.13)") – If validation of the input arguments fail.

* **neo4j.exceptions.ClientError** – If creation of vector index fails.

Return type:

None

neo4j\_graphrag.indexes.create\_fulltext\_index(_driver_, _name_, _label_, _node\_properties_, _fail\_if\_exists\=False_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/indexes.html#create_fulltext_index)

This method constructs a Cypher query and executes it to create a new fulltext index in Neo4j.

See Cypher manual on [creating fulltext indexes](https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/full-text-indexes/#create-full-text-indexes).

Ensure that the index name provided is unique within the database context.

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.indexes import create_fulltext_index

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

INDEX_NAME = "fulltext-index-name"

# Connect to Neo4j database
driver = GraphDatabase.driver(URI, auth=AUTH)

# Creating the index
create_fulltext_index(
    driver,
    INDEX_NAME,
    label="Document",
    node_properties=["vectorProperty"],
    fail_if_exists=False,
)

```

Parameters:

* **driver** (_neo4j.Driver_) – Neo4j Python driver instance.

* **name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The unique name of the index.

* **label** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The node label to be indexed.

* **node\_properties** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – The node properties to create the fulltext index on.

* **fail\_if\_exists** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")) – If True raise an error if the index already exists. Defaults to False.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Raises:

* [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError "(in Python v3.13)") – If validation of the input arguments fail.

* **neo4j.exceptions.ClientError** – If creation of fulltext index fails.

Return type:

None

neo4j\_graphrag.indexes.drop\_index\_if\_exists(_driver_, _name_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/indexes.html#drop_index_if_exists)

This method constructs a Cypher query and executes it to drop an index in Neo4j, if the index exists. See Cypher manual on [dropping vector indexes](https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/vector-indexes/#drop-vector-indexes).

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.indexes import drop_index_if_exists

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

INDEX_NAME = "fulltext-index-name"

# Connect to Neo4j database
driver = GraphDatabase.driver(URI, auth=AUTH)

# Dropping the index if it exists
drop_index_if_exists(
    driver,
    INDEX_NAME,
)

```

Parameters:

* **driver** (_neo4j.Driver_) – Neo4j Python driver instance.

* **name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the index to delete.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Raises:

**neo4j.exceptions.ClientError** – If dropping of index fails.

Return type:

None

neo4j\_graphrag.indexes.upsert\_vectors(_driver_, _ids_, _embedding\_property_, _embeddings_, _neo4j\_database\=None_, _entity\_type\=EntityType.NODE_)
[\[source\]](about:blank/_modules/neo4j_graphrag/indexes.html#upsert_vectors)

This method constructs a Cypher query and executes it to upsert (insert or update) embeddings on a set of nodes or relationships.

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.indexes import upsert_vectors

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

# Connect to Neo4j database
driver = GraphDatabase.driver(URI, auth=AUTH)

# Upsert embeddings data for several nodes
upsert_vectors(
    driver,
    ids=['123', '456', '789'],
    embedding_property="vectorProperty",
    embeddings=[
        [0.12, 0.34, 0.56],
        [0.78, 0.90, 0.12],
        [0.34, 0.56, 0.78],
    ],
    neo4j_database="neo4j",
    entity_type='NODE',
)

```

Parameters:

* **driver** (_neo4j.Driver_) – Neo4j Python driver instance.

* **ids** (_List__\[_[_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")_\]_) – The element IDs of the nodes or relationships.

* **embedding\_property** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the property to store the vectors in.

* **embeddings** (_List__\[**List**\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]__\]_) – The list of vectors to store, one per ID.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – The name of the Neo4j database. If not provided, defaults to the server’s default database. ‘neo4j’ by default.

* **entity\_type** (_EntityType_) – Specifies whether to upsert to nodes (‘NODE’) or relationships (‘RELATIONSHIP’). Defaults to ‘NODE’.

Raises:

* [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError "(in Python v3.13)") – If the lengths of IDs and embeddings do not match, or if embeddings are not of uniform dimension.

* [**Neo4jInsertionError**](#neo4j_graphrag.exceptions.Neo4jInsertionError "neo4j_graphrag.exceptions.Neo4jInsertionError") – If an error occurs while attempting to upsert the vectors in Neo4j.

Return type:

None

neo4j\_graphrag.indexes.upsert\_vector(_driver_, _node\_id_, _embedding\_property_, _vector_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/indexes.html#upsert_vector)

Warning

‘upsert\_vector’ is deprecated and will be removed in a future version, please use ‘upsert\_vectors’ instead.

This method constructs a Cypher query and executes it to upsert (insert or update) a vector property on a specific node.

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.indexes import upsert_vector

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

# Connect to Neo4j database
driver = GraphDatabase.driver(URI, auth=AUTH)

# Upsert the vector data
upsert_vector(
    driver,
    node_id="nodeId",
    embedding_property="vectorProperty",
    vector=...,
)

```

Parameters:

* **driver** (_neo4j.Driver_) – Neo4j Python driver instance.

* **node\_id** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – The element id of the node.

* **embedding\_property** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the property to store the vector in.

* **vector** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]_) – The vector to store.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Raises:

[**Neo4jInsertionError**](#neo4j_graphrag.exceptions.Neo4jInsertionError "neo4j_graphrag.exceptions.Neo4jInsertionError") – If upserting of the vector fails.

Return type:

None

neo4j\_graphrag.indexes.upsert\_vector\_on\_relationship(_driver_, _rel\_id_, _embedding\_property_, _vector_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/indexes.html#upsert_vector_on_relationship)

Warning

‘upsert\_vector\_on\_relationship’ is deprecated and will be removed in a future version, please use ‘upsert\_vectors’ instead.

This method constructs a Cypher query and executes it to upsert (insert or update) a vector property on a specific relationship.

Example:

```
from neo4j import GraphDatabase
from neo4j_graphrag.indexes import upsert_vector_on_relationship

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

# Connect to Neo4j database
driver = GraphDatabase.driver(URI, auth=AUTH)

# Upsert the vector data
upsert_vector_on_relationship(
    driver,
    node_id="nodeId",
    embedding_property="vectorProperty",
    vector=...,
)

```

Parameters:

* **driver** (_neo4j.Driver_) – Neo4j Python driver instance.

* **rel\_id** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – The element id of the relationship.

* **embedding\_property** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the property to store the vector in.

* **vector** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]_) – The vector to store.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Raises:

[**Neo4jInsertionError**](#neo4j_graphrag.exceptions.Neo4jInsertionError "neo4j_graphrag.exceptions.Neo4jInsertionError") – If upserting of the vector fails.

Return type:

None

_async_ neo4j\_graphrag.indexes.async\_upsert\_vector(_driver_, _node\_id_, _embedding\_property_, _vector_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/indexes.html#async_upsert_vector)

Warning

‘async\_upsert\_vector’ is deprecated and will be removed in a future version.

This method constructs a Cypher query and asynchronously executes it to upsert (insert or update) a vector property on a specific node.

Example:

```
from neo4j import AsyncGraphDatabase
from neo4j_graphrag.indexes import upsert_vector

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

# Connect to Neo4j database
driver = AsyncGraphDatabase.driver(URI, auth=AUTH)

# Upsert the vector data
async_upsert_vector(
    driver,
    node_id="nodeId",
    embedding_property="vectorProperty",
    vector=...,
)

```

Parameters:

* **driver** (_neo4j.AsyncDriver_) – Neo4j Python asynchronous driver instance.

* **node\_id** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – The element id of the node.

* **embedding\_property** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the property to store the vector in.

* **vector** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]_) – The vector to store.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Raises:

[**Neo4jInsertionError**](#neo4j_graphrag.exceptions.Neo4jInsertionError "neo4j_graphrag.exceptions.Neo4jInsertionError") – If upserting of the vector fails.

Return type:

None

_async_ neo4j\_graphrag.indexes.async\_upsert\_vector\_on\_relationship(_driver_, _rel\_id_, _embedding\_property_, _vector_, _neo4j\_database\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/indexes.html#async_upsert_vector_on_relationship)

Warning

‘async\_upsert\_vector\_on\_relationship’ is deprecated and will be removed in a future version.

This method constructs a Cypher query and asynchronously executes it to upsert (insert or update) a vector property on a specific relationship.

Example:

```
from neo4j import AsyncGraphDatabase
from neo4j_graphrag.indexes import upsert_vector_on_relationship

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

# Connect to Neo4j database
driver = AsyncGraphDatabase.driver(URI, auth=AUTH)

# Upsert the vector data
async_upsert_vector_on_relationship(
    driver,
    node_id="nodeId",
    embedding_property="vectorProperty",
    vector=...,
)

```

Parameters:

* **driver** (_neo4j.AsyncDriver_) – Neo4j Python asynchronous driver instance.

* **rel\_id** ([_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")) – The element id of the relationship.

* **embedding\_property** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the property to store the vector in.

* **vector** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]_) – The vector to store.

* **neo4j\_database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) –

    The name of the Neo4j database. If not provided, this defaults to the server’s default database (“neo4j” by default) ([see reference to documentation](https://neo4j.com/docs/operations-manual/current/database-administration/#manage-databases-default)).

Raises:

[**Neo4jInsertionError**](#neo4j_graphrag.exceptions.Neo4jInsertionError "neo4j_graphrag.exceptions.Neo4jInsertionError") – If upserting of the vector fails.

Return type:

None

neo4j\_graphrag.indexes.retrieve\_vector\_index\_info(_driver_, _index\_name_, _label\_or\_type_, _embedding\_property_)
[\[source\]](about:blank/_modules/neo4j_graphrag/indexes.html#retrieve_vector_index_info)

Check if a vector index exists in a Neo4j database and return its information. If no matching index is found, returns None.

Parameters:

* **driver** (_neo4j.Driver_) – Neo4j Python driver instance.

* **index\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the index to look up.

* **label\_or\_type** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The label (for nodes) or type (for relationships) of the index.

* **embedding\_property** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the property containing the embeddings.

Returns:

A dictionary containing the first matching index’s information if found, or None otherwise.

Return type:

Optional\[Dict\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"), Any\]\]

neo4j\_graphrag.indexes.retrieve\_fulltext\_index\_info(_driver_, _index\_name_, _label\_or\_type_, _text\_properties\=\[\]_)
[\[source\]](about:blank/_modules/neo4j_graphrag/indexes.html#retrieve_fulltext_index_info)

Check if a full text index exists in a Neo4j database and return its information. If no matching index is found, returns None.

Parameters:

* **driver** (_neo4j.Driver_) – Neo4j Python driver instance.

* **index\_name** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The name of the index to look up.

* **label\_or\_type** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")) – The label (for nodes) or type (for relationships) of the index.

* **text\_properties** (_List__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – The names of the text properties indexed.

Returns:

A dictionary containing the first matching index’s information if found, or None otherwise.

Return type:

Optional\[Dict\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"), Any\]\]

neo4j\_graphrag.schema.get\_structured\_schema(_driver_, _is\_enhanced\=False_, _database\=None_, _timeout\=None_, _sanitize\=False_)
[\[source\]](about:blank/_modules/neo4j_graphrag/schema.html#get_structured_schema)

Returns the structured schema of the graph.

Returns a dict with following format:

```
{
    'node_props': {
        'Person': [{'property': 'id', 'type': 'INTEGER'}, {'property': 'name', 'type': 'STRING'}]
    },
    'rel_props': {
        'KNOWS': [{'property': 'fromDate', 'type': 'DATE'}]
    },
    'relationships': [
        {'start': 'Person', 'type': 'KNOWS', 'end': 'Person'}
    ],
    'metadata': {
        'constraint': [
            {'id': 7, 'name': 'person_id', 'type': 'UNIQUENESS', 'entityType': 'NODE', 'labelsOrTypes': ['Persno'], 'properties': ['id'], 'ownedIndex': 'person_id', 'propertyType': None},
        ],
        'index': [
            {'label': 'Person', 'properties': ['name'], 'size': 2, 'type': 'RANGE', 'valuesSelectivity': 1.0, 'distinctValues': 2.0},
        ]
    }
}

```

Note

The internal structure of the returned dict depends on the apoc.meta.data and apoc.schema.nodes procedures.

Warning

Some labels are excluded from the output schema:

* The \_\_Entity\_\_ and \_\_KGBuilder\_\_ node labels which are created by the KG Builder pipeline within this package

* Some labels related to Bloom internals.

Parameters:

* **driver** (_neo4j.Driver_) – Neo4j Python driver instance.

* **is\_enhanced** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")) – Flag indicating whether to format the schema with detailed statistics (True) or in a simpler overview format (False).

* **database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – The name of the database to connect to. Default is ‘neo4j’.

* **timeout** (_Optional__\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]_) – The timeout for transactions in seconds. Useful for terminating long-running queries. By default, there is no timeout set.

* **sanitize** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")) – A flag to indicate whether to remove lists with more than 128 elements from results. Useful for removing embedding-like properties from database responses. Default is False.

Returns:

the graph schema information in a structured format.

Return type:

[dict](https://docs.python.org/3/library/stdtypes.html#dict "(in Python v3.13)")\[[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)"), Any\]

neo4j\_graphrag.schema.get\_schema(_driver_, _is\_enhanced\=False_, _database\=None_, _timeout\=None_, _sanitize\=False_)
[\[source\]](about:blank/_modules/neo4j_graphrag/schema.html#get_schema)

Returns the schema of the graph as a string with following format:

```
Node properties:
Person {id: INTEGER, name: STRING}
Relationship properties:
KNOWS {fromDate: DATE}
The relationships:
(:Person)-[:KNOWS]->(:Person)

```

Parameters:

* **driver** (_neo4j.Driver_) – Neo4j Python driver instance.

* **is\_enhanced** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")) – Flag indicating whether to format the schema with detailed statistics (True) or in a simpler overview format (False).

* **database** (_Optional__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_\]_) – The name of the database to connect to. Default is ‘neo4j’.

* **timeout** (_Optional__\[_[_float_](https://docs.python.org/3/library/functions.html#float "(in Python v3.13)")_\]_) – The timeout for transactions in seconds. Useful for terminating long-running queries. By default, there is no timeout set.

* **sanitize** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")) – A flag to indicate whether to remove lists with more than 128 elements from results. Useful for removing embedding-like properties from database responses. Default is False.

Returns:

the graph schema information in a serialized format.

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

neo4j\_graphrag.schema.format\_schema(_schema_, _is\_enhanced_)
[\[source\]](about:blank/_modules/neo4j_graphrag/schema.html#format_schema)

Format the structured schema into a human-readable string.

Depending on the is\_enhanced flag, this function either creates a concise listing of node labels and relationship types alongside their properties or generates an enhanced, more verbose representation with additional details like example or available values and min/max statistics. It also includes a formatted list of existing relationships.

Parameters:

* **schema** (_Dict__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _Any__\]_) – The structured schema dictionary, containing properties for nodes and relationships as well as relationship definitions.

* **is\_enhanced** ([_bool_](https://docs.python.org/3/library/functions.html#bool "(in Python v3.13)")) – Flag indicating whether to format the schema with detailed statistics (True) or in a simpler overview format (False).

Returns:

A formatted string representation of the graph schema, including node properties, relationship properties, and relationship patterns.

Return type:

[str](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")

Message History
-----------------------------------------------------------

_class_ neo4j\_graphrag.message\_history.InMemoryMessageHistory(_messages\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/message_history.html#InMemoryMessageHistory)

Message history stored in memory

Example:

```
from neo4j_graphrag.message_history import InMemoryMessageHistory
from neo4j_graphrag.types import LLMMessage

history = InMemoryMessageHistory()

message = LLMMessage(role="user", content="Hello!")
history.add_message(message)

```

Parameters:

**messages** (_Optional__\[**List**\[_[_LLMMessage_](about:blank/types.html#neo4j_graphrag.types.LLMMessage "neo4j_graphrag.types.LLMMessage")_\]__\]_) – List of messages to initialize the history with. Defaults to None.

_class_ neo4j\_graphrag.message\_history.Neo4jMessageHistory(_session\_id_, _driver_, _window\=None_)
[\[source\]](about:blank/_modules/neo4j_graphrag/message_history.html#Neo4jMessageHistory)

Message history stored in a Neo4j database

Example:

```
import neo4j
from neo4j_graphrag.message_history import Neo4jMessageHistory
from neo4j_graphrag.types import LLMMessage

driver = neo4j.GraphDatabase.driver(URI, auth=AUTH)

history = Neo4jMessageHistory(
    session_id="123", driver=driver, window=10
)

message = LLMMessage(role="user", content="Hello!")
history.add_message(message)

```

Parameters:

* **session\_id** (_Union__\[_[_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ [_int_](https://docs.python.org/3/library/functions.html#int "(in Python v3.13)")_\]_) – Unique identifier for the chat session.

* **driver** (_neo4j.Driver_) – Neo4j driver instance.

* **node\_label** ([_str_](https://docs.python.org/3/library/stdtypes.html#str "(in Python v3.13)")_,_ _optional_) – Label used for session nodes in Neo4j. Defaults to “Session”.

* **window** (_Optional__\[**PositiveInt**\]__,_ _optional_) – Number of previous messages to return when retrieving messages.

Errors
-----------------------------------------

* [`neo4j_graphrag.exceptions.Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

  * [`neo4j_graphrag.exceptions.RetrieverInitializationError`](#neo4j_graphrag.exceptions.RetrieverInitializationError "neo4j_graphrag.exceptions.RetrieverInitializationError")

  * [`neo4j_graphrag.exceptions.EmbeddingsGenerationError`](#neo4j_graphrag.exceptions.EmbeddingsGenerationError "neo4j_graphrag.exceptions.EmbeddingsGenerationError")

  * [`neo4j_graphrag.exceptions.SearchValidationError`](#neo4j_graphrag.exceptions.SearchValidationError "neo4j_graphrag.exceptions.SearchValidationError")

  * [`neo4j_graphrag.exceptions.FilterValidationError`](#neo4j_graphrag.exceptions.FilterValidationError "neo4j_graphrag.exceptions.FilterValidationError")

  * [`neo4j_graphrag.exceptions.EmbeddingRequiredError`](#neo4j_graphrag.exceptions.EmbeddingRequiredError "neo4j_graphrag.exceptions.EmbeddingRequiredError")

  * [`neo4j_graphrag.exceptions.InvalidRetrieverResultError`](#neo4j_graphrag.exceptions.InvalidRetrieverResultError "neo4j_graphrag.exceptions.InvalidRetrieverResultError")

  * [`neo4j_graphrag.exceptions.Neo4jIndexError`](#neo4j_graphrag.exceptions.Neo4jIndexError "neo4j_graphrag.exceptions.Neo4jIndexError")

  * [`neo4j_graphrag.exceptions.Neo4jVersionError`](#neo4j_graphrag.exceptions.Neo4jVersionError "neo4j_graphrag.exceptions.Neo4jVersionError")

  * [`neo4j_graphrag.exceptions.Text2CypherRetrievalError`](#neo4j_graphrag.exceptions.Text2CypherRetrievalError "neo4j_graphrag.exceptions.Text2CypherRetrievalError")

  * [`neo4j_graphrag.exceptions.SchemaFetchError`](#neo4j_graphrag.exceptions.SchemaFetchError "neo4j_graphrag.exceptions.SchemaFetchError")

  * [`neo4j_graphrag.exceptions.RagInitializationError`](#neo4j_graphrag.exceptions.RagInitializationError "neo4j_graphrag.exceptions.RagInitializationError")

  * [`neo4j_graphrag.exceptions.PromptMissingInputError`](#neo4j_graphrag.exceptions.PromptMissingInputError "neo4j_graphrag.exceptions.PromptMissingInputError")

  * [`neo4j_graphrag.exceptions.LLMGenerationError`](#neo4j_graphrag.exceptions.LLMGenerationError "neo4j_graphrag.exceptions.LLMGenerationError")

  * [`neo4j_graphrag.exceptions.SchemaValidationError`](#neo4j_graphrag.exceptions.SchemaValidationError "neo4j_graphrag.exceptions.SchemaValidationError")

  * [`neo4j_graphrag.exceptions.PdfLoaderError`](#neo4j_graphrag.exceptions.PdfLoaderError "neo4j_graphrag.exceptions.PdfLoaderError")

  * [`neo4j_graphrag.exceptions.PromptMissingPlaceholderError`](#neo4j_graphrag.exceptions.PromptMissingPlaceholderError "neo4j_graphrag.exceptions.PromptMissingPlaceholderError")

  * [`neo4j_graphrag.exceptions.InvalidHybridSearchRankerError`](#neo4j_graphrag.exceptions.InvalidHybridSearchRankerError "neo4j_graphrag.exceptions.InvalidHybridSearchRankerError")

  * [`neo4j_graphrag.exceptions.SearchQueryParseError`](#neo4j_graphrag.exceptions.SearchQueryParseError "neo4j_graphrag.exceptions.SearchQueryParseError")

  * [`neo4j_graphrag.experimental.pipeline.exceptions.PipelineDefinitionError`](#neo4j_graphrag.experimental.pipeline.exceptions.PipelineDefinitionError "neo4j_graphrag.experimental.pipeline.exceptions.PipelineDefinitionError")

  * [`neo4j_graphrag.experimental.pipeline.exceptions.PipelineMissingDependencyError`](#neo4j_graphrag.experimental.pipeline.exceptions.PipelineMissingDependencyError "neo4j_graphrag.experimental.pipeline.exceptions.PipelineMissingDependencyError")

  * [`neo4j_graphrag.experimental.pipeline.exceptions.PipelineStatusUpdateError`](#neo4j_graphrag.experimental.pipeline.exceptions.PipelineStatusUpdateError "neo4j_graphrag.experimental.pipeline.exceptions.PipelineStatusUpdateError")

  * [`neo4j_graphrag.experimental.pipeline.exceptions.InvalidJSONError`](#neo4j_graphrag.experimental.pipeline.exceptions.InvalidJSONError "neo4j_graphrag.experimental.pipeline.exceptions.InvalidJSONError")

### Neo4jGraphRagError

_class_ neo4j\_graphrag.exceptions.Neo4jGraphRagError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#Neo4jGraphRagError)

Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception "(in Python v3.13)")

Global exception used for the neo4j-graphrag package.

### RetrieverInitializationError

_class_ neo4j\_graphrag.exceptions.RetrieverInitializationError(_errors_)
[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#RetrieverInitializationError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when initialization of a retriever fails.

Parameters:

**errors** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[**ErrorDetails**\]_)

### SearchValidationError

_class_ neo4j\_graphrag.exceptions.SearchValidationError(_errors_)
[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#SearchValidationError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised for validation errors during search.

Parameters:

**errors** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[**ErrorDetails**\]_)

### FilterValidationError

_class_ neo4j\_graphrag.exceptions.FilterValidationError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#FilterValidationError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when input validation for metadata filtering fails.

### EmbeddingsGenerationError

_class_ neo4j\_graphrag.exceptions.EmbeddingsGenerationError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#EmbeddingsGenerationError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when generation of embeddings fails

### EmbeddingRequiredError

_class_ neo4j\_graphrag.exceptions.EmbeddingRequiredError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#EmbeddingRequiredError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when an embedding method is required but not provided.

### InvalidRetrieverResultError

_class_ neo4j\_graphrag.exceptions.InvalidRetrieverResultError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#InvalidRetrieverResultError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when the Retriever fails to return a result.

### Neo4jIndexError

_class_ neo4j\_graphrag.exceptions.Neo4jIndexError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#Neo4jIndexError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when handling Neo4j index fails.

### Neo4jInsertionError

_class_ neo4j\_graphrag.exceptions.Neo4jInsertionError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#Neo4jInsertionError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when inserting data into the Neo4j database fails.

### Neo4jVersionError

_class_ neo4j\_graphrag.exceptions.Neo4jVersionError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#Neo4jVersionError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when Neo4j version does not meet minimum requirements.

### Text2CypherRetrievalError

_class_ neo4j\_graphrag.exceptions.Text2CypherRetrievalError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#Text2CypherRetrievalError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when text-to-cypher retrieval fails.

### SchemaFetchError

_class_ neo4j\_graphrag.exceptions.SchemaFetchError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#SchemaFetchError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when a Neo4jSchema cannot be fetched.

### RagInitializationError

_class_ neo4j\_graphrag.exceptions.RagInitializationError(_errors_)
[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#RagInitializationError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Parameters:

**errors** ([_list_](https://docs.python.org/3/library/stdtypes.html#list "(in Python v3.13)")_\[**ErrorDetails**\]_)

### PromptMissingInputError

_class_ neo4j\_graphrag.exceptions.PromptMissingInputError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#PromptMissingInputError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when a prompt required input is missing.

### LLMGenerationError

_class_ neo4j\_graphrag.exceptions.LLMGenerationError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#LLMGenerationError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when answer generation from LLM fails.

### SchemaValidationError

_class_ neo4j\_graphrag.exceptions.SchemaValidationError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#SchemaValidationError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Custom exception for errors in schema configuration.

### PdfLoaderError

_class_ neo4j\_graphrag.exceptions.PdfLoaderError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#PdfLoaderError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Custom exception for errors in PDF loader.

### PromptMissingPlaceholderError

_class_ neo4j\_graphrag.exceptions.PromptMissingPlaceholderError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#PromptMissingPlaceholderError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when a prompt is missing an expected placeholder.

### InvalidHybridSearchRankerError

_class_ neo4j\_graphrag.exceptions.InvalidHybridSearchRankerError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#InvalidHybridSearchRankerError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when an invalid ranker type for Hybrid Search is provided.

### SearchQueryParseError

_class_ neo4j\_graphrag.exceptions.SearchQueryParseError[\[source\]](about:blank/_modules/neo4j_graphrag/exceptions.html#SearchQueryParseError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Exception raised when there is a query parse error in the text search string.

### PipelineDefinitionError

_class_ neo4j\_graphrag.experimental.pipeline.exceptions.PipelineDefinitionError[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/exceptions.html#PipelineDefinitionError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Raised when the pipeline graph is invalid

### PipelineMissingDependencyError

_class_ neo4j\_graphrag.experimental.pipeline.exceptions.PipelineMissingDependencyError[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/exceptions.html#PipelineMissingDependencyError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Raised when a task is scheduled but its dependencies are not yet done

### PipelineStatusUpdateError

_class_ neo4j\_graphrag.experimental.pipeline.exceptions.PipelineStatusUpdateError[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/exceptions.html#PipelineStatusUpdateError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Raises when trying an invalid change of state (e.g. DONE => DOING)

### InvalidJSONError

_class_ neo4j\_graphrag.experimental.pipeline.exceptions.InvalidJSONError[\[source\]](about:blank/_modules/neo4j_graphrag/experimental/pipeline/exceptions.html#InvalidJSONError)

Bases: [`Neo4jGraphRagError`](#neo4j_graphrag.exceptions.Neo4jGraphRagError "neo4j_graphrag.exceptions.Neo4jGraphRagError")

Raised when JSON repair fails to produce valid JSON.
