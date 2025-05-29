import datetime
import csv
from databricks import sql

server_hostname = ""
http_path = ""
access_token = ""
CHUNK_SIZE = 10000 
OUTPUT_FILE = 'hco_contacts_report_null_fields.csv'

def generate_csv_chunks(cursor):
    column_names = [desc[0] for desc in cursor.description]
    
    yield column_names

    while True:
        rows = cursor.fetchmany(CHUNK_SIZE)
        if not rows:
            break
        for row in rows:
          yield row

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
        query = "SELECT hco_contacts_first FROM masterfile_reports.report_builder.hco_contacts_report LIMIT 300000"
        cursor.execute(query)

        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:
            csv_writer = csv.writer(outfile, delimiter=',')
            for csv_row in generate_csv_chunks(cursor):
                csv_writer.writerow(csv_row)

    print(f"CSV guardado en {OUTPUT_FILE}")

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