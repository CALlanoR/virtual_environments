import sys
from pymilvus import MilvusClient, DataType


def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <opción>")
        print("Opciones disponibles:")
        print("  1 - Create schema and collection")
        print("  2 - list collections")
        sys.exit(1)

    try:
        opcion = int(sys.argv[1])
    except ValueError:
        print("Error: La opción debe ser un número")
        sys.exit(1)

    if opcion == 1:
        create_schema_and_collection()
    elif opcion == 2:
        list_and_describe_collections()
    else:
        print(f"Error: Opción {opcion} no válida")
        print("Opciones disponibles: 1, 2")
        sys.exit(1)


def create_schema_and_collection():
    client = MilvusClient(
        uri="http://localhost:19530",
        token="root:Milvus"
    )

    schema = MilvusClient.create_schema(
        auto_id=False,
        enable_dynamic_field=True,
    )

    schema.add_field(field_name="my_id", datatype=DataType.INT64, is_primary=True)
    schema.add_field(field_name="my_vector", datatype=DataType.FLOAT_VECTOR, dim=5)
    schema.add_field(field_name="my_varchar", datatype=DataType.VARCHAR, max_length=512)

    index_params = client.prepare_index_params()

    index_params.add_index(
        field_name="my_id",
        index_type="AUTOINDEX"
    )

    index_params.add_index(
        field_name="my_vector", 
        index_type="AUTOINDEX",
        metric_type="COSINE"
    )

    client.create_collection(
        collection_name="customized_setup_1",
        schema=schema,
        index_params=index_params
    )

    res = client.get_load_state(
        collection_name="customized_setup_1"
    )

    print(res)


def list_and_describe_collections():
    client = MilvusClient(
        uri="http://localhost:19530",
        token="root:Milvus"
    )

    res = client.list_collections()

    print(res)


if __name__ == "__main__":
    main()
