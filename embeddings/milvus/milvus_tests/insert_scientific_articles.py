from pymilvus import connections, Collection, model

MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "scientific_articles_index"
VECTOR_DIMENSION = 1024  # BGE-M3 uses 1024 dimensions for dense embeddings

print("Loading BGE-M3 embedding model...")
bge_m3_ef = model.hybrid.BGEM3EmbeddingFunction(
    model_name='BAAI/bge-m3',  # BGE-M3 model
    device='cpu',               # Use 'cuda:0' for GPU
    use_fp16=False             # Set to True if using GPU for better performance
)
print(f"Model loaded successfully. Dense dimension: {bge_m3_ef.dim['dense']}")

# Sample scientific articles data
articles_data = [
    {
        "opensearch_ref_id": "art_001",
        "article_title": "Deep Learning Approaches for Medical Image Segmentation",
        "summary": "This paper reviews recent advances in deep learning techniques for medical image segmentation. We examine convolutional neural networks, U-Net architectures, and attention mechanisms that have shown promising results in identifying anatomical structures and pathological regions in CT, MRI, and X-ray images.",
        "authors_list": ["John Smith", "Maria Garcia", "Wei Chen"],
        "publication_year": 2023,
        "publisher_name": "Nature Medicine",
        "identifiers_json": {
            "DOI": "10.1038/s41591-023-00001-1",
            "PMID": "37123456",
            "PMCID": "PMC9876543"
        },
        "mesh_terms": ["Deep Learning", "Image Processing", "Convolutional Neural Networks", "Medical Imaging", "Radiology", "Diagnostic Imaging"]
    },
    {
        "opensearch_ref_id": "art_002",
        "article_title": "CRISPR-Cas9 Gene Editing: Current Applications and Future Perspectives",
        "summary": "CRISPR-Cas9 technology has revolutionized gene editing capabilities. This review discusses its applications in treating genetic disorders, cancer research, and agricultural improvements. We also address ethical considerations and regulatory challenges facing this transformative technology.",
        "authors_list": ["Sarah Johnson", "Robert Lee", "Anna Kowalski", "Ahmed Hassan"],
        "publication_year": 2024,
        "publisher_name": "Cell",
        "identifiers_json": {
            "DOI": "10.1016/j.cell.2024.01.001",
            "PMID": "38234567",
            "PMCID": "PMC10123456"
        },
        "mesh_terms": ["CRISPR-Cas Systems", "Gene Editing", "Genetic Therapy", "Genetic Engineering", "Molecular Biology", "Cancer Research"]
    },
    {
        "opensearch_ref_id": "art_003",
        "article_title": "Climate Change Impact on Marine Ecosystems: A Global Analysis",
        "summary": "Rising ocean temperatures and acidification are causing significant disruptions to marine ecosystems worldwide. This study presents a comprehensive analysis of coral bleaching events, fish migration patterns, and plankton population changes observed over the past three decades across different oceanic regions.",
        "authors_list": ["Elena Rodriguez", "James Wilson", "Yuki Tanaka"],
        "publication_year": 2023,
        "publisher_name": "Science",
        "identifiers_json": {
            "DOI": "10.1126/science.abcd1234",
            "PMID": "37345678",
            "PMCID": "PMC9987654"
        },
        "mesh_terms": ["Climate Change", "Marine Biology", "Ecosystem", "Ocean Temperature", "Coral Reefs", "Marine Ecology", "Global Warming"]
    },
    {
        "opensearch_ref_id": "art_004",
        "article_title": "Quantum Computing Algorithms for Drug Discovery",
        "summary": "Quantum computing offers unprecedented computational power for molecular simulations and drug discovery. This paper introduces novel quantum algorithms for protein folding prediction and drug-target interaction analysis, demonstrating significant speedups compared to classical approaches in pharmaceutical research applications.",
        "authors_list": ["David Brown", "Priya Sharma"],
        "publication_year": 2024,
        "publisher_name": "Nature Quantum",
        "identifiers_json": {
            "DOI": "10.1038/s41567-024-02345-6",
            "PMID": "38456789",
            "PMCID": "PMC10234567"
        },
        "mesh_terms": ["Quantum Computing", "Drug Discovery", "Protein Folding", "Computational Biology", "Pharmaceutical Research", "Algorithms"]
    },
    {
        "opensearch_ref_id": "art_005",
        "article_title": "Microbiome Influence on Human Mental Health and Behavior",
        "summary": "The gut-brain axis represents a bidirectional communication system between the gastrointestinal tract and the central nervous system. This research explores how gut microbiota composition affects mental health conditions including depression, anxiety, and neurodegenerative diseases through various biochemical pathways.",
        "authors_list": ["Michael Thompson", "Lisa Anderson", "Carlos Martinez", "Fatima Al-Rahman", "Hiroshi Nakamura"],
        "publication_year": 2023,
        "publisher_name": "Lancet Neurology",
        "identifiers_json": {
            "DOI": "10.1016/S1474-4422(23)00123-4",
            "PMID": "37567890",
            "PMCID": "PMC10001234"
        },
        "mesh_terms": ["Microbiota", "Gut-Brain Axis", "Mental Health", "Depression", "Anxiety", "Neuroscience", "Gastrointestinal Microbiome"]
    }
]

def generate_embedding(article):
    """
    Generate dense embedding vector using BGE-M3 model.
    Combines title and summary to create a comprehensive representation.
    BGE-M3 generates both dense and sparse embeddings for hybrid search.
    """
    # Combine title and summary for embedding
    text_for_embedding = f"{article['article_title']} {article['summary']}"

    # Generate embeddings using BGE-M3
    # encode_documents returns dict with 'dense' and 'sparse' embeddings
    embeddings = bge_m3_ef.encode_documents([text_for_embedding])

    # Extract the dense embedding (1024 dimensions)
    dense_embedding = embeddings['dense'][0]

    return dense_embedding

def prepare_data_for_insertion(articles):
    """
    Prepare data in the format required by Milvus for insertion.
    """
    data = []

    for article in articles:
        print(f"Generating embedding for: {article['article_title'][:50]}...")

        article_vector = generate_embedding(article)

        data.append({
            "opensearch_ref_id": article["opensearch_ref_id"],
            "article_vector": article_vector,
            "publication_year": article["publication_year"],
            "publisher_name": article["publisher_name"],
            "identifiers_json": article["identifiers_json"],
            "article_title": article["article_title"],
            "authors_list": article["authors_list"],
            "summary": article["summary"],
            "mesh_terms": article["mesh_terms"]
        })

    return data

# Main execution
print(f"\nConnecting to Milvus at {MILVUS_HOST}:{MILVUS_PORT}...")
try:
    connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
    print("Successfully connected to Milvus.")

    # Load the collection
    collection = Collection(COLLECTION_NAME)
    print(f"Collection '{COLLECTION_NAME}' loaded.")

    # Prepare data for insertion
    print("\nPreparing articles data and generating embeddings...")
    data_to_insert = prepare_data_for_insertion(articles_data)

    # Insert data into the collection
    print(f"\nInserting {len(data_to_insert)} articles into the collection...")
    insert_result = collection.insert(data_to_insert)
    print(f"Successfully inserted {len(insert_result.primary_keys)} articles.")
    print(f"Primary keys: {insert_result.primary_keys}")

    # Flush to ensure data is persisted
    collection.flush()
    print("Data flushed to storage.")

    # Get collection statistics
    print(f"\nCollection statistics:")
    print(f"Total entities: {collection.num_entities}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Disconnect
    connections.disconnect("default")
    print("\nDisconnected from Milvus.")
