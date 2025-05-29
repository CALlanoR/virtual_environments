import datetime
import json
from databricks import sql

server_hostname = ""
http_path = ""
access_token = ""
CHUNK_SIZE = 200 
OUTPUT_FILE = 'output.json'

def row_to_dict(column_names, row):
    return dict(zip(column_names, row))

def generate_json_chunks(cursor):
    column_names = [desc[0] for desc in cursor.description]
    first_chunk = True
    while True:
        rows = cursor.fetchmany(CHUNK_SIZE)
        if not rows:
            break
        
        json_chunk = ',\n'.join(json.dumps(row_to_dict(column_names, row), default=str) for row in rows)
        if first_chunk:
            yield '[' + json_chunk  # add '[' at the beginning of the chunk
            first_chunk = False
        else:
            yield json_chunk
    yield ']'

try:
    start = datetime.datetime.now()
    print("------------- start --------------")
    print(str(start))

    connection = sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        access_token=access_token
    )

    print("Conexión establecida con Databricks.")

    with connection.cursor() as cursor:
        query = "SELECT * FROM masterfile_reports.report_builder.hcp_reference_report LIMIT 1000"
        cursor.execute(query)

        with open(OUTPUT_FILE, 'w') as outfile:
          for json_chunk in generate_json_chunks(cursor):
            outfile.write(json_chunk)

    print(f"JSON guardado en {OUTPUT_FILE}")

    end = datetime.datetime.now()
    print("--------------------------------------")
    print(str(end))
    elapsed = end - start
    print("elapsed seconds: " + str(elapsed))
    print("--------------- end -------------------")

except Exception as e:
    print(f"Error al conectarse o ejecutar el query: {e}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("Conexión cerrada.")