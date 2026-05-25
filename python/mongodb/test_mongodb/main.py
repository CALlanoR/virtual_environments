import pymongo
from datetime import datetime, UTC
from bson.objectid import ObjectId
from pymongo import MongoClient, TEXT

# 1. Database Connection Initialization
try:
    client = MongoClient("mongodb://admin:password123@localhost:27017/")
    db_name = 'GobiernoDB'
    
    # Check if the database already exists in the cluster
    existing_dbs = client.list_database_names()
    print(f"Existing databases: {existing_dbs}")
    
    if db_name not in existing_dbs:
        print(f"Database '{db_name}' does not exist. Initializing creation...")
    else:
        print(f"Database '{db_name}' already exists.")

    # Note: MongoDB creates the DB/Collection only when the first document is inserted.
    db = client[db_name]
    contracts = db['ContratosPublicos']
    
except Exception as e:
    print(f"Connection failed: {e}")


# 2. Text Index Creation for Full-Text Search
# Essential for efficient keyword searching within high-volume datasets
contracts.create_index([("description", TEXT), ("name", TEXT)])

def insert_contracts():
    """Inserts public sector contract data in Spanish."""
    documents = [
        {
            "nombre": "Modernización de Red Eléctrica - Fase I",
            "entidad": "Ministerio de Energía",
            "descripcion": "Contrato para la actualización de infraestructura de red en zonas rurales.",
            "monto": 5000000,
            "fecha": datetime.now(UTC),
            "tags": ["infraestructura", "energía", "rural", "modernización", "licitación-abierta"]
        },
        {
            "nombre": "Suministro de Alimentos Escolares 2026",
            "entidad": "Secretaría de Educación",
            "descripcion": "Provisión de raciones alimentarias para instituciones públicas del sector norte.",
            "monto": 1200000,
            "fecha": datetime.now(UTC),
            "tags": ["educación", "bienestar", "logística", "salud", "anual"]
        }
    ]
    result = contracts.insert_many(documents)
    print(f"Data ingestion complete. Inserted IDs: {result.inserted_ids}")

def insert_contracts2():
    """Inserts public sector contract data in Spanish."""
    documents = [
        {
            "nombre": "Juegos panamericanos 2026",
            "entidad": "Secretaría de Deportes",
            "descripcion": "Organización de los juegos panamericanos 2026.",
            "monto": 1200000,
            "fecha": datetime.now(UTC),
            "tags": ["deportes", "juegos", "panamericanos", "anual"]
        }
    ]
    result = contracts.insert_many(documents)
    print(f"Data ingestion complete. Inserted IDs: {result.inserted_ids}")


def search_all_fields(word):
    """Searches for a word across all string fields of every document (case-insensitive)."""
    print(f"\n--- Search results for word: '{word}' in all fields ---")
    regex = {"$regex": word, "$options": "i"}
    query = {
        "$or": [
            {"nombre": regex},
            {"entidad": regex},
            {"descripcion": regex},
        ]
    }
    results = list(contracts.find(query))
    if results:
        for doc in results:
            print(f"Nombre: {doc['nombre']}\n Entidad: {doc['entidad']}\n Descripcion: {doc['descripcion']}\n Monto: {doc['monto']}\n Fecha: {doc['fecha']}\n Tags: {doc['tags']}")
    else:
        print("No documents found.")
    return results


def search_by_tag(tag_value):
    """Searches for documents that contain a specific value in the 'tags' array."""
    print(f"\n--- Search results for tag: '{tag_value}' ---")
    query = {"tags": tag_value}
    results = list(contracts.find(query))
    if results:
        for doc in results:
            print(f"Nombre: {doc['nombre']}\n Entidad: {doc['entidad']}\n Descripcion: {doc['descripcion']}\n Monto: {doc['monto']}\n Fecha: {doc['fecha']}\n Tags: {doc['tags']}")
    else:
        print("No documents found with that tag.")
    return results


def update_document_field(doc_id, field, new_value):
    """Updates any field of a document found by its _id.
    
    Args:
        doc_id: The MongoDB _id of the document (string or ObjectId).
        field: The field name to update (e.g. 'monto', 'entidad', 'descripcion').
        new_value: The new value to set for the field.
    """
    # Convert string to ObjectId if necessary
    if isinstance(doc_id, str):
        doc_id = ObjectId(doc_id)

    print(f"\n--- Updating field '{field}' for document _id: {doc_id} ---")

    # Step 1: Find the document before updating
    query = {"_id": doc_id}
    doc_before = contracts.find_one(query)

    if not doc_before:
        print(f"No document found with _id: {doc_id}")
        return None

    print(f"\n[BEFORE] Nombre: {doc_before['nombre']}")
    print(f"  {field}: {doc_before.get(field, 'FIELD NOT FOUND')}")

    # Step 2: Update the field using $set
    result = contracts.update_one(query, {"$set": {field: new_value}})
    print(f"\nMatched: {result.matched_count}, Modified: {result.modified_count}")

    # Step 3: Retrieve and show the updated document
    doc_after = contracts.find_one(query)
    print(f"\n[AFTER]  Nombre: {doc_after['nombre']}")
    print(f"  {field}: {doc_after.get(field, 'FIELD NOT FOUND')}")

    return doc_after


# Execution Entry Point
if __name__ == "__main__":
    # insert_contracts()
    # insert_contracts2()
    results = search_all_fields("infraestructura")
    input("press any key to continue...")
    results =search_by_tag("juegos")
    # Update using the _id from the first search result
    if results:
        doc_id = results[0]["_id"]
        update_document_field(doc_id, "monto", 7500000)