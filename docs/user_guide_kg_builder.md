# User Guide: Knowledge Graph Builder — neo4j-graphrag-python documentation

## Overview

This page provides information about how to create a Knowledge Graph from unstructured data.

> **Warning:** This feature is still experimental. API changes and bug fixes are expected.

## Pipeline Structure

A Knowledge Graph (KG) construction pipeline requires a few components (some of the below components are optional):

* **Data loader**: extract text from files (PDFs, …)
* **Text splitter**: split the text into smaller pieces of text (chunks), manageable by the LLM context window (token limit)
* **Chunk embedder** (optional): compute the chunk embeddings
* **Schema builder**: provide a schema to ground the LLM extracted entities and relations and obtain an easily navigable KG
* **Lexical graph builder**: build the lexical graph (Document, Chunk and their relationships) (optional)
* **Entity and relation extractor**: extract relevant entities and relations from the text
* **Knowledge Graph writer**: save the identified entities and relations
* **Entity resolver**: merge similar entities into a single node

![KG Builder pipeline](_images/kg_builder_pipeline.png)

This package contains the interface and implementations for each of these components, which are detailed in the following sections.

To see an end-to-end example of a Knowledge Graph construction pipeline, visit the [example folder](https://github.com/neo4j/neo4j-graphrag-python/blob/main/examples/) in the project's GitHub repository.

## Simple KG Pipeline

The simplest way to begin building a KG from unstructured data using this package is utilizing the SimpleKGPipeline interface:

```python
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline

kg_builder = SimpleKGPipeline(
    llm=llm, # an LLMInterface for Entity and Relation extraction
    driver=neo4j_driver,  # a neo4j driver to write results to graph
    embedder=embedder,  # an Embedder for chunks
    from_pdf=True,   # set to False if parsing an already extracted text
)
await kg_builder.run_async(file_path=str(file_path))
# await kg_builder.run_async(text="my text")  # if using from_pdf=False
```

See:

* [Using Another LLM Model](./user_guide_rag.md#using-another-llm-model) to learn how to instantiate the llm
* [Embedders](./user_guide_rag.md#embedders) to learn how to instantiate the embedder

The following section outlines the configuration parameters for this class.

### Customizing the SimpleKGPipeline

#### Graph Schema

It is possible to guide the LLM by supplying a list of entities, relationships, and instructions on how to connect them. However, note that the extracted graph may not fully adhere to these guidelines. Entities and relationships can be represented as either simple strings (for their labels) or dictionaries. If using a dictionary, it must include a label key and can optionally include description and properties keys, as shown below:

```python
ENTITIES = [
    # entities can be defined with a simple label...
    "Person",
    # ... or with a dict if more details are needed,
    # such as a description:
    {"label": "House", "description": "Family the person belongs to"},
    # or a list of properties the LLM will try to attach to the entity:
    {"label": "Planet", "properties": [{"name": "weather", "type": "STRING"}]},
]
# same thing for relationships:
RELATIONS = [
    "PARENT_OF",
    {
        "label": "HEIR_OF",
        "description": "Used for inheritor relationship between father and sons",
    },
    {"label": "RULES", "properties": [{"name": "fromYear", "type": "INTEGER"}]},
]
```

The potential_schema is defined by a list of triplet in the format: (source_node_label, relationship_label, target_node_label). For instance:

```python
POTENTIAL_SCHEMA = [
    ("Person", "PARENT_OF", "Person"),
    ("Person", "HEIR_OF", "House"),
    ("House", "RULES", "Planet"),
]
```

This schema information can be provided to the SimpleKGBuilder as demonstrated below:

```python
kg_builder = SimpleKGPipeline(
    # ...
    entities=ENTITIES,
    relations=RELATIONS,
    potential_schema=POTENTIAL_SCHEMA,
    # ...
)
```

#### Skip Entity Resolution

By default, after each run, an Entity Resolution step is performed to merge nodes that share the same label and name property. To disable this behavior, adjust the following parameter:

```python
kg_builder = SimpleKGPipeline(
    # ...
    perform_entity_resolution=False,
    # ...
)
```

#### Neo4j Database

To write to a non-default Neo4j database, specify the database name using this parameter:

```python
kg_builder = SimpleKGPipeline(
    # ...
    neo4j_database="myDb",
    # ...
)
```

#### Using Custom Components

For advanced customization or when using a custom implementation, you can pass instances of specific components to the SimpleKGPipeline. The components that can customized at the moment are:

* text_splitter: must be an instance of [TextSplitter](./api.md#textsplitter)
* pdf_loader: must be an instance of [PdfLoader](./api.md#pdfloader)
* kg_writer: must be an instance of [KGWriter](./api.md#kgwriter)

For instance, the following code can be used to customize the chunk size and chunk overlap in the text splitter component:

```python
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import (
    FixedSizeSplitter,
)

text_splitter = FixedSizeSplitter(chunk_size=500, chunk_overlap=100)

kg_builder = SimpleKGPipeline(
    # ...
    text_splitter=text_splitter,
    # ...
)
```

### Using a Config file

```python
from neo4j_graphrag.experimental.pipeline.config.runner import PipelineRunner

file_path = "my_config.json"

pipeline = PipelineRunner.from_config_file(file_path)
await pipeline.run({"text": "my text"})
```

The config file can be written in either JSON or YAML format.

Here is an example of a base configuration file in JSON format:

```json
{
    "version_": 1,
    "template_": "SimpleKGPipeline",
    "neo4j_config": {},
    "llm_config": {},
    "embedder_config": {}
}
```

And like this in YAML:

```yaml
version_: 1
template_: SimpleKGPipeline
neo4j_config:
llm_config:
embedder_config:
```

#### Defining a Neo4j Driver

Below is an example of configuring a Neo4j driver in a JSON configuration file:

```json
{
    "neo4j_config": {
        "params_": {
            "uri": "bolt://...",
            "user": "neo4j",
            "password": "password"
        }
    }
}
```

Same for YAML:

```yaml
neo4j_config:
    params_:
        uri: bolt://
        user: neo4j
        password: password
```

In some cases, it may be necessary to avoid hard-coding sensitive values, such as passwords or API keys, to ensure security. To address this, the configuration parser supports parameter resolution methods.

#### Parameter resolution

To instruct the configuration parser to read a parameter from an environment variable, use the following syntax:

```json
{
    "neo4j_config": {
        "params_": {
            "uri": "bolt://...",
            "user": "neo4j",
            "password": {
                "resolver_": "ENV",
                "key": "NEO4J_PASSWORD"
            }
        }
    }
}
```

And for YAML:

```yaml
neo4j_config:
  params_:
    uri: bolt://
    user: neo4j
    password:
      resolver_: ENV
      key: NEO4J_PASSWORD
```

* The resolver_=ENV key is mandatory and its value cannot be altered.
* The key specifies the name of the environment variable to be read.

This syntax can be applied to all parameters.

#### Defining an LLM

Below is an example of configuring an LLM in a JSON configuration file:

```json
{
    "llm_config": {
        "class_": "OpenAILLM",
        "params_": {
            "mode_name": "gpt-4o",
            "api_key": {
                "resolver_": "ENV",
                "var_": "OPENAI_API_KEY",
            },
            "model_params": {
                "temperature": 0,
                "max_tokens": 2000,
                "response_format": {"type": "json_object"}
            }
        }
    }
}
```

And the equivalent YAML:

```yaml
llm_config:
  class_: OpenAILLM
  params_:
    model_name: gpt-4o
    api_key:
      resolver_: ENV
      var_: OPENAI_API_KEY
    model_params:
      temperature: 0
      max_tokens: 2000
      response_format:
        type: json_object
```

* The class_ key specifies the path to the class to be instantiated.
* The params_ key contains the parameters to be passed to the class constructor.

When using an LLM implementation provided by this package, the full path in the class_key can be omitted (the parser will automatically import from neo4j_graphrag.llm). For custom implementations, the full path must be explicitly specified, for example: my_package.my_llm.MyLLM.

Warning

Check the [Installation](./index.md#installation) section to make sure you have the required dependencies installed when using an LLM.

#### Defining an Embedder

The same principles apply to embedder_config:

```json
{
    "embedder_config": {
        "class_": "OpenAIEmbeddings",
        "params_": {
            "mode": "text-embedding-ada-002",
            "api_key": {
                "resolver_": "ENV",
                "var_": "OPENAI_API_KEY",
            }
        }
    }
}
```

Or the YAML version:

```yaml
embedder_config:
  class_: OpenAIEmbeddings
  params_:
    api_key:
      resolver_: ENV
      var_: OPENAI_API_KEY
```

* For embedder implementations from this package, the full path can be omitted in the class_key (the parser will import from neo4j_graphrag.embeddings).
* For custom implementations, the full path must be provided, for example: my_package.my_embedding.MyEmbedding.

#### Other configuration

The other parameters exposed in the [SimpleKGPipeline](./api.md#simplekgpipeline) can also be configured within the configuration file.

```json
{
    "from_pdf": false,
    "perform_entity_resolution": true,
    "neo4j_database": "myDb",
    "on_error": "IGNORE",
    "prompt_template": "...",
    "entities": [
        "Person",
        {
            "label": "House",
            "description": "Family the person belongs to",
            "properties": [
                {"name": "name", "type": "STRING"}
            ]
        },
        {
            "label": "Planet",
            "properties": [
                {"name": "name", "type": "STRING"},
                {"name": "weather", "type": "STRING"}
            ]
        }
    ],
    "relations": [
        "PARENT_OF",
        {
            "label": "HEIR_OF",
            "description": "Used for inheritor relationship between father and sons"
        },
        {
            "label": "RULES",
            "properties": [
                {"name": "fromYear", "type": "INTEGER"}
            ]
        }
    ],
    "potential_schema": [
        ["Person", "PARENT_OF", "Person"],
        ["Person", "HEIR_OF", "House"],
        ["House", "RULES", "Planet"]
    ],
    "lexical_graph_config": {
        "chunk_node_label": "TextPart"
    }
}
```

or in YAML:

```yaml
from_pdf: false
perform_entity_resolution: true
neo4j_database: myDb
on_error: IGNORE
prompt_template: ...
entities:
  - label: Person
  - label: House
    description: Family the person belongs to
    properties:
      - name: name
        type: STRING
  - label: Planet
    properties:
      - name: name
        type: STRING
      - name: weather
        type: STRING
relations:
  - label: PARENT_OF
  - label: HEIR_OF
    description: Used for inheritor relationship between father and sons
  - label: RULES
    properties:
      - name: fromYear
        type: INTEGER
potential_schema:
  - ["Person", "PARENT_OF", "Person"]
  - ["Person", "HEIR_OF", "House"]
  - ["House", "RULES", "Planet"]
lexical_graph_config:
    chunk_node_label: TextPart
```

It is also possible to further customize components, with a syntax similar to the one used for llm_config or embedder_config:

```json
{
    "text_splitter": {
        "class_": "text_splitters.FixedSizeSplitter",
        "params_": {
            "chunk_size": 500,
            "chunk_overlap": 100
        }
    }
}
```

The YAML equivalent:

```yaml
text_splitter:
  class_: text_splitters.fixed_size_splitter.FixedSizeSplitter
  params_:
    chunk_size: 100
    chunk_overlap: 10
```

The neo4j_graphrag.experimental.components prefix will be appended automatically if needed.

Knowledge Graph Builder Components
-------------------------------------------------------------------------------------------------

Below is a list of the different components available in this package and how to use them.

Each of these components can be run individually:

```python
import asyncio
from neo4j_graphrag.experimental.components.pdf_loader import PdfLoader
my_component = PdfLoader()
asyncio.run(my_component.run("my_file.pdf"))
```

They can also be used within a pipeline:

```python
from neo4j_graphrag.experimental.pipeline import Pipeline
from neo4j_graphrag.experimental.components.pdf_loader import PdfLoader
pipeline = Pipeline()
my_component = PdfLoader()
pipeline.add_component(my_component, "component_name")
```

### Data Loader

Data loaders start from a file path and return the text extracted from this file.

This package currently supports text extraction from PDFs:

```python
from pathlib import Path
from neo4j_graphrag.experimental.components.pdf_loader import PdfLoader

loader = PdfLoader()
await loader.run(path=Path("my_file.pdf"))
```

To implement your own loader, use the DataLoader interface:

```python
from pathlib import Path
from neo4j_graphrag.experimental.components.pdf_loader import DataLoader, PdfDocument

class MyDataLoader(DataLoader):
    async def run(self, path: Path) -> PdfDocument:
        # process file in `path`
        return PdfDocument(text="text")
```

### Text Splitter

Document splitters, as the name indicate, split documents into smaller chunks that can be processed within the LLM token limits:

```python
from neo4j_graphrag.experimental.components.text_splitters.fixed_size_splitter import FixedSizeSplitter

splitter = FixedSizeSplitter(chunk_size=4000, chunk_overlap=200, approximate=False)
splitter.run(text="Hello World. Life is beautiful.")
```

Note

approximate flag is by default set to True to ensure clean chunk start and end (i.e. avoid words cut in the middle) whenever it is possible.

Wrappers for LangChain and LlamaIndex text splitters are included in this package:

```python
from langchain_text_splitters import CharacterTextSplitter
from neo4j_graphrag.experimental.components.text_splitters.langchain import LangChainTextSplitterAdapter
splitter = LangChainTextSplitterAdapter(
    CharacterTextSplitter(chunk_size=4000, chunk_overlap=200, separator=".")
)
await splitter.run(text="Hello World. Life is beautiful.")
```

Also see [LangChainTextSplitterAdapter](./api.md#langchaintextsplitteradapter) and [LlamaIndexTextSplitterAdapter](./api.md#llamaindextextsplitteradapter).

To implement a custom text splitter, the TextSplitter interface can be used:

```python
from neo4j_graphrag.experimental.components.text_splitters.base import TextSplitter
from neo4j_graphrag.experimental.components.types import TextChunks, TextChunk


class MyTextSplitter(TextSplitter):

    def __init__(self, separator: str = ".") -> None:
        self.separator = separator

    async def run(self, text: str) -> TextChunks:
         return TextChunks(
             chunks=[
                 TextChunk(text=text_chunk)
                 for text_chunk in text.split(self.separator)
             ]
         )
```

### Chunk Embedder

In order to embed the chunks' texts (to be used in vector search RAG), one can use the TextChunkEmbedder component, which rely on the [Embedder](./api.md#embedder) interface.

Example usage:

```python
from neo4j_graphrag.experimental.components.embedder import TextChunkEmbedder
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings
text_chunk_embedder = TextChunkEmbedder(embedder=OpenAIEmbeddings())
await text_chunk_embedder.run(text_chunks=TextChunks(chunks=[TextChunk(text="my_text")]))
```

Note

To use OpenAI (embedding or LLM), the OPENAI_API_KEY must be in the env vars, for instance using:

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."
```

If OpenAI is not an option, see [Embedders](./user_guide_rag.md#embedders) to learn how to use other supported embedders.

The embeddings are added to each chunk metadata, and will be saved as a Chunk node property in the graph if create_lexical_graph is enabled in the EntityRelationExtractor (keep reading).

### Lexical Graph Builder

Once the chunks are extracted and embedded (if required), a graph can be created.

The **lexical graph** contains:

* Document node: represent the processed document and have a path property.
* Chunk nodes: represent the text chunks. They have a text property and, if computed, an embedding property.
* NEXT_CHUNK relationships between one chunk node and the next one in the document. It can be used to enhance the context in a RAG application.
* FROM_DOCUMENT relationship between each chunk and the document it was built from.

Example usage:

```python
from neo4j_graphrag.experimental.pipeline.components.lexical_graph_builder import LexicalGraphBuilder
from neo4j_graphrag.experimental.pipeline.components.types import LexicalGraphConfig

lexical_graph_builder = LexicalGraphBuilder(config=LexicalGraphConfig())
graph = await lexical_graph_builder.run(
    text_chunks=TextChunks(chunks=[
        TextChunk(text="some text", index=0),
        TextChunk(text="some text", index=1),
    ]),
    document_info=DocumentInfo(path="my_document.pdf"),
)
```

See [Knowledge Graph Writer](#kg-writer-section) to learn how to write the resulting nodes and relationships to Neo4j.

### Neo4j Chunk Reader

The Neo4j chunk reader component is used to read text chunks from Neo4j. Text chunks can be created by the lexical graph builder or another process.

```python
import neo4j
from neo4j_graphrag.experimental.components.neo4j_reader import Neo4jChunkReader
from neo4j_graphrag.experimental.components.types import LexicalGraphConfig

reader = Neo4jChunkReader(driver)
result = await reader.run()
```

#### Configure node labels and relationship types

Optionally, the document and chunk node labels can be configured using a LexicalGraphConfig object:

```python
from neo4j_graphrag.experimental.components.neo4j_reader import Neo4jChunkReader
from neo4j_graphrag.experimental.components.types import LexicalGraphConfig, TextChunks

# optionally, define a LexicalGraphConfig object
# shown below with the default values
config = LexicalGraphConfig(
    chunk_node_label="Chunk",
    document_node_label="Document",
    chunk_to_document_relationship_type="PART_OF_DOCUMENT",
    next_chunk_relationship_type="NEXT_CHUNK",
    node_to_chunk_relationship_type="PART_OF_CHUNK",
    chunk_embedding_property="embeddings",
)
reader = Neo4jChunkReader(driver)
result = await reader.run(lexical_graph_config=config)
```

### Schema Builder

The schema is used to try and ground the LLM to a list of possible entities and relations of interest. So far, schema must be manually created by specifying:

* **Entities** the LLM should look for in the text, including their properties (name and type).
* **Relations** of interest between these entities, including the relation properties (name and type).
* **Triplets** to define the start (source) and end (target) entity types for each relation.

Here is a code block illustrating these concepts:

```python
from neo4j_graphrag.experimental.components.schema import (
    SchemaBuilder,
    SchemaEntity,
    SchemaProperty,
    SchemaRelation,
)

schema_builder = SchemaBuilder()

await schema_builder.run(
    entities=[
        SchemaEntity(
            label="Person",
            properties=[
                SchemaProperty(name="name", type="STRING"),
                SchemaProperty(name="place_of_birth", type="STRING"),
                SchemaProperty(name="date_of_birth", type="DATE"),
            ],
        ),
        SchemaEntity(
            label="Organization",
            properties=[
                SchemaProperty(name="name", type="STRING"),
                SchemaProperty(name="country", type="STRING"),
            ],
        ),
    ],
    relations=[
        SchemaRelation(
            label="WORKED_ON",
        ),
        SchemaRelation(
            label="WORKED_FOR",
        ),
    ],
    possible_schema=[
        ("Person", "WORKED_ON", "Field"),
        ("Person", "WORKED_FOR", "Organization"),
    ],
)
```

After validation, this schema is saved in a SchemaConfig object, whose dict representation is passed to the LLM.

### Entity and Relation Extractor

This component is responsible for extracting the relevant entities and relationships from each text chunk, using the schema as guideline.

This package contains an LLM-based entity and relationships extractor: LLMEntityRelationExtractor. It can be used in this way:

```python
from neo4j_graphrag.experimental.components.entity_relation_extractor import (
    LLMEntityRelationExtractor,
)
from neo4j_graphrag.llm import OpenAILLM

extractor = LLMEntityRelationExtractor(
    llm=OpenAILLM(
        model_name="gpt-4o",
        model_params={
            "max_tokens": 1000,
            "response_format": {"type": "json_object"},
        },
    )
)
await extractor.run(chunks=TextChunks(chunks=[TextChunk(text="some text")]))
```

Warning

Using OpenAILLM requires the openai Python client. You can install it with pip install "neo4j_graphrag[openai]".

Warning

The LLMEntityRelationExtractor works better if "response_format": {"type": "json_object"} is in the model parameters.

The LLM to use can be customized, the only constraint is that it obeys the [LLMInterface](./api.md#llminterface).

#### Schema Enforcement Behaviour

By default, even if a schema is provided to guide the LLM in the entity and relation extraction, the LLM response is not validated against that schema. This behaviour can be changed by using the enforce_schema flag in the LLMEntityRelationExtractor constructor:

```python
from neo4j_graphrag.experimental.components.entity_relation_extractor import LLMEntityRelationExtractor
from neo4j_graphrag.experimental.components.types import SchemaEnforcementMode

extractor = LLMEntityRelationExtractor(
    # ...
    enforce_schema=SchemaEnforcementMode.STRICT,
)
```

In this scenario, any extracted node/relation/property that is not part of the provided schema will be pruned. Any relation whose start node or end node does not conform to the provided tuple in potential_schema will be pruned. If a relation start/end nodes are valid but the direction is incorrect, the latter will be inverted. If a node is left with no properties, it will be also pruned.

Warning

Note that if the schema enforcement mode is on but the schema is not provided, no schema enforcement will be applied.

#### Error Behaviour

By default, if the extraction fails for one chunk, it will be ignored and the non-failing chunks will be saved. This behaviour can be changed by using the on_error flag in the LLMEntityRelationExtractor constructor:

```python
from neo4j_graphrag.experimental.components.entity_relation_extractor import (
    LLMEntityRelationExtractor,
    OnError,
)

extractor = LLMEntityRelationExtractor(
    # ...
    on_error=OnError.RAISE,
)
```

In this scenario, any failing chunk will make the whole pipeline fail (for all chunks), and no data will be saved to Neo4j.

#### Lexical Graph

By default, the LLMEntityRelationExtractor also creates the [lexical graph](#lexical-graph-builder).

If this 'lexical graph' is not desired, set the created_lexical_graph to False in the extractor constructor:

```python
extractor = LLMEntityRelationExtractor(
    llm=....,
    create_lexical_graph=False,
)
```

Note

* If self.create_lexical_graph is set to True, the complete lexical graph will be created, including the document and chunk nodes, along with the relationships between entities and the chunk they were extracted from.
* If self.create_lexical_graph is set to False but lexical_graph_config is provided, the document and chunk nodes won't be created. However, relationships between chunks and the entities extracted from them will still be added to the graph.

Warning

If omitting self.create_lexical_graph and the chunk does not exist, this will result in no relationship being created in the database by the writer.

#### Customizing the Prompt

The default prompt uses the [ERExtractionTemplate](./api.md#erextractiontemplate). It is possible to provide a custom prompt as string:

```python
extractor = LLMEntityRelationExtractor(
    llm=....,
    prompt="Extract entities from {text}",
)
```

The following variables can be used in the prompt:

* text (str): the text to be analyzed (mandatory).
* schema (str): the graph schema to be used.
* examples (str): examples for few-shot learning.

### Knowledge Graph Writer

KG writer are used to save the results of the EntityRelationExtractor. The main implementation is the Neo4jWriter that will write nodes and relationships to a Neo4j database:

```python
import neo4j
from neo4j_graphrag.experimental.components.kg_writer import Neo4jWriter
from neo4j_graphrag.experimental.components.types import Neo4jGraph

with neo4j.GraphDatabase.driver(
    "bolt://localhost:7687", auth=("neo4j", "password")
) as driver:
    writer = Neo4jWriter(driver)
    graph = Neo4jGraph(nodes=[], relationships=[])
    await writer.run(graph)
```

Adjust the batch_size parameter of Neo4jWriter to optimize insert performance. This parameter controls the number of nodes or relationships inserted per batch, with a default value of 1000.

See [Neo4jGraph](./types.md#neo4jgraph).

It is possible to create a custom writer using the KGWriter interface:

```python
import json
from pydantic import validate_call
from neo4j_graphrag.experimental.components.kg_writer import KGWriter

class JsonWriter(KGWriter):

    def __init__(self, file_name: str) -> None:
        self.file_name = file_name

    @validate_call
    async def run(self, graph: Neo4jGraph) -> KGWriterModel:
        try:
            with open(self.file_name, "w") as f:
                json.dump(graph.model_dump(), f, indent=2)
            return KGWriterModel(status="SUCCESS")
        except Exception:
            return KGWriterModel(status="FAILURE")
```

Note

The validate_call decorator is required when the input parameter contain a Pydantic model.

See [KGWriterModel](./types.md#kgwritermodel) and [KGWriter](./api.md#kgwriter) in API reference.

### Entity Resolver

The KG Writer component creates new nodes for each identified entity without making assumptions about entity similarity. The Entity Resolver is responsible for refining the created knowledge graph by merging entity nodes that represent the same real-world object.

In practice, this package implements a simple resolver that merges nodes with the same label and identical "name" property.

Warning

The SinglePropertyExactMatchResolver **replaces** the nodes created by the KG writer.

It can be used like this:

```python
from neo4j_graphrag.experimental.components.resolver import (
    SinglePropertyExactMatchResolver,
)
resolver = SinglePropertyExactMatchResolver(driver)
res = await resolver.run()
```

Warning

By default, all nodes with the **Entity** label will be resolved. This behavior can be controled using the filter_query parameter described below.

#### Filter Query Parameter

To exclude specific nodes from the resolution, a filter_query can be added to the query. For example, if a :Resolved label has been applied to already resolved entities in the graph, these entities can be excluded with the following approach:

```python
from neo4j_graphrag.experimental.components.resolver import (
    SinglePropertyExactMatchResolver,
)
filter_query = "WHERE NOT entity:Resolved"
resolver = SinglePropertyExactMatchResolver(driver, filter_query=filter_query)
res = await resolver.run()
```

Similar approach can be used to exclude entities created from a previous pipeline run on the same document, assuming a label OldDocument has been assigned to the previously created document node:

```python
filter_query = "WHERE NOT EXISTS((entity)-[:FROM_DOCUMENT]->(:OldDocument))"
```
