from pymilvus import connections, Collection, model
import sys

MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "scientific_articles_index"

# Initialize the BGE-M3 embedding model
print("Loading BGE-M3 embedding model...")
bge_m3_ef = model.hybrid.BGEM3EmbeddingFunction(
    model_name='BAAI/bge-m3',
    device='cpu',
    use_fp16=False
)
print(f"Model loaded successfully. Dense dimension: {bge_m3_ef.dim['dense']}")


def generate_query_embedding(query_text):
    """
    Generate embedding for the search query using BGE-M3 model.
    """
    embeddings = bge_m3_ef.encode_queries([query_text])
    query_embedding = embeddings['dense'][0]
    return query_embedding


def search_articles(query_text, top_k=5):
    """
    Search for articles similar to the query text.

    Args:
        query_text: The search query string
        top_k: Number of top results to return (default: 5)

    Returns:
        List of search results with article data and similarity scores
    """
    print(f"\nGenerating embedding for query: '{query_text}'")
    query_vector = generate_query_embedding(query_text)

    print(f"\nConnecting to Milvus at {MILVUS_HOST}:{MILVUS_PORT}...")
    connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
    print("Successfully connected to Milvus.")

    # Load the collection
    collection = Collection(COLLECTION_NAME)
    collection.load()
    print(f"Collection '{COLLECTION_NAME}' loaded.")

    # Define search parameters
    search_params = {
        "metric_type": "COSINE",
        "params": {"nprobe": 10}
    }

    # Define which fields to return
    output_fields = [
        "opensearch_ref_id",
        "article_title",
        "summary",
        "authors_list",
        "publication_year",
        "publisher_name",
        "mesh_terms",
        "identifiers_json"
    ]

    # Perform the search
    print(f"\nSearching for top {top_k} similar articles...")
    results = collection.search(
        data=[query_vector],
        anns_field="article_vector",
        param=search_params,
        limit=top_k,
        output_fields=output_fields
    )

    # Disconnect
    connections.disconnect("default")

    return results


def display_results(results):
    """
    Display search results in a readable format.
    """
    print("\n" + "="*80)
    print("SEARCH RESULTS")
    print("="*80)

    for idx, hits in enumerate(results):
        print(f"\nQuery {idx + 1} returned {len(hits)} results:\n")

        for rank, hit in enumerate(hits, 1):
            print(f"\n--- Result #{rank} ---")
            print(f"Score (Similarity): {hit.score:.4f}")
            print(f"ID: {hit.entity.get('opensearch_ref_id')}")
            print(f"Title: {hit.entity.get('article_title')}")
            print(f"Authors: {', '.join(hit.entity.get('authors_list', []))}")
            print(f"Year: {hit.entity.get('publication_year')}")
            print(f"Publisher: {hit.entity.get('publisher_name')}")
            print(f"MeSH Terms: {', '.join(hit.entity.get('mesh_terms', []))}")
            print(f"\nSummary: {hit.entity.get('summary')}")

            identifiers = hit.entity.get('identifiers_json', {})
            if identifiers:
                print(f"\nIdentifiers:")
                print(f"  DOI: {identifiers.get('DOI', 'N/A')}")
                print(f"  PMID: {identifiers.get('PMID', 'N/A')}")
                print(f"  PMCID: {identifiers.get('PMCID', 'N/A')}")

            print("-" * 80)


def main():
    """
    Main function to handle command-line queries or interactive mode.
    """
    if len(sys.argv) > 1:
        # Query provided as command-line argument
        query = " ".join(sys.argv[1:])
        top_k = 5
    else:
        # Interactive mode
        print("\n" + "="*80)
        print("SCIENTIFIC ARTICLES VECTOR SEARCH")
        print("="*80)
        query = input("\nEnter your search query: ").strip()

        if not query:
            print("Error: Query cannot be empty")
            sys.exit(1)

        try:
            top_k = int(input("Number of results to return (default 5): ").strip() or "5")
        except ValueError:
            top_k = 5
            print("Invalid number, using default: 5")

    try:
        # Perform the search
        results = search_articles(query, top_k)

        # Display results
        display_results(results)

        print(f"\n✓ Search completed successfully!")

    except Exception as e:
        print(f"\n✗ Error during search: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


# Buscar artículos sobre inteligencia artificial en medicina
# python query_scientific_articles.py "artificial intelligence diagnosis"

# Buscar sobre microbioma
# python query_scientific_articles.py "gut bacteria mental health"