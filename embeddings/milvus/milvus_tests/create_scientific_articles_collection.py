from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection
)

MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"

COLLECTION_NAME = "scientific_articles_index"
VECTOR_DIMENSION = 1024 # BGE-M3 model uses 1024 dimensions for dense embeddings

# Crear los campos del esquema de la colección
fields = [
    FieldSchema(
        name="opensearch_ref_id", 
        dtype=DataType.VARCHAR, 
        is_primary=True, 
        auto_id=False, 
        max_length=256,
        description="OpenSearch Id)"
    ),
    
    FieldSchema(
        name="article_dense_vector",
        dtype=DataType.FLOAT_VECTOR,
        dim=VECTOR_DIMENSION,
        description="Dense vector embedding using BGE-M3 model (title + summary)"
    ),

    FieldSchema(
        name="article_sparse_vector",
        dtype=DataType.SPARSE_FLOAT_VECTOR,
        description="Sparse vector embedding using BGE-M3 model for hybrid search"
    ),

    FieldSchema(
        name="publication_year", 
        dtype=DataType.INT64,
        description="publication year of the article"
    ),

    FieldSchema(
        name="publisher_name", 
        dtype=DataType.VARCHAR, 
        max_length=128,
        description="publisher of the article"
    ),

    FieldSchema(
        name="identifiers_json", 
        dtype=DataType.JSON,
        description="Contains DOI, PMCID, PMID as a JSON object"
    ),
    
    FieldSchema(
        name="article_title",
        dtype=DataType.VARCHAR,
        max_length=512,
        description="Title of the article"
    ),

    FieldSchema(
        name="authors_list",
        dtype=DataType.ARRAY,
        element_type=DataType.VARCHAR,
        max_capacity=100,
        max_length=256,
        description="List of authors of the article"
    ),

    FieldSchema(
        name="summary",
        dtype=DataType.VARCHAR,
        max_length=1000,
        description="Summary or abstract of the article"
    ),

    FieldSchema(
        name="mesh_terms",
        dtype=DataType.ARRAY,
        element_type=DataType.VARCHAR,
        max_capacity=50,
        max_length=128,
        description="Medical Subject Headings (MeSH) terms associated with the article"
    ),
]

# Crear el esquema de la colección
schema = CollectionSchema(
    fields, 
    description="Collection of embeddings of scientific articles with filtered metadata.",
    enable_dynamic_field=True # Permite guardar otros datos no definidos si es necesario
)

# 3. Conectar a Milvus
print(f"Connecting to Milvus at {MILVUS_HOST}:{MILVUS_PORT}...")
try:
    connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
    print("Successfully connected to Milvus.")

    # 4. Check if the collection already exists
    if utility.has_collection(COLLECTION_NAME):
        print(f"The collection '{COLLECTION_NAME}' already exists. Dropping to recreate...")
        # First, release the collection from memory if it's loaded
        existing_collection = Collection(COLLECTION_NAME)
        existing_collection.release()
        print("Collection released from memory.")
        # Now drop the collection
        utility.drop_collection(COLLECTION_NAME)
        print("Collection dropped successfully.")

    # 5. Create the collection
    collection = Collection(
        name=COLLECTION_NAME, 
        schema=schema, 
        using='default'
    )
    print(f"Collection '{COLLECTION_NAME}' created successfully.")

    # 6. Create indexes on the vector fields
    # Dense vector index - Using IVF_FLAT for dense embeddings
    dense_index_params = {
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024},
        "metric_type": "COSINE"  # Using Cosine Similarity for embeddings
    }

    collection.create_index(
        field_name="article_dense_vector",
        index_params=dense_index_params
    )
    print("Index created on the 'article_dense_vector' field.")

    # Sparse vector index - Using SPARSE_INVERTED_INDEX for sparse embeddings
    sparse_index_params = {
        "index_type": "SPARSE_INVERTED_INDEX",
        "metric_type": "IP"  # Inner Product for sparse vectors
    }

    collection.create_index(
        field_name="article_sparse_vector",
        index_params=sparse_index_params
    )
    print("Index created on the 'article_sparse_vector' field.")

    # 7. Load the collection into memory (for immediate searches)
    collection.load()
    print("Collection loaded into memory. Ready for data insertion.")

except Exception as e:
    print(f"Error: {e}")
finally:
    # Optional: Disconnect
    connections.disconnect("default")


# PubMed
# ======
# opensearch_ref_id  --- PMID.#text
# article_dense_vector (mesh + article_title + authors_list + summary + keywords)
# article_sparse_vector
# publication_year
# publisher_name
# identifiers_json (doi, pmid, pmcid)
# article_title
# authors_list
# summary
# mesh_terms --- vector
# keywords (MedlineCitation.KeywordList.Keyword)


# ClinicalTrials
# ==============
# opensearch_ref_id
# article_dense_vector (mesh + conditions + interventions + official_title + overall_officials)
# article_sparse_vector
# status  (figma aparece como Trial Status)
# start_date (año de publicacion)
# phase (figma aparece como Trail phase)
# nct_id (igual figma que opensearch)
# brief_summary
# overall_officials si en official_role dice PRINCIPAL_INVESTIGATOR entonces se retorna official_name y official_affiliation (estos son investigadores)
# mesh_terms ---- vector
# conditions
# interventions.intervention_name
# brief_title
# official_title ---- vector