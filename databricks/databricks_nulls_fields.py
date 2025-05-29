import datetime
import csv
from databricks import sql
import pandas as pd

server_hostname = ""
http_path = ""
access_token = ""
CHUNK_SIZE = 10000 
OUTPUT_FILE = 'hcp_reference_report_nulls_fields.csv'


try:
    start = datetime.datetime.now()
    print("------------- start --------------")
    print(str(start))

    with sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        access_token=access_token
    ) as connection:

        print("Conexión establecida con Databricks.")

        with connection.cursor() as cursor:
            query = "SELECT * FROM masterfile_reports.report_builder.hcp_reference_report LIMIT 1000000"
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

            df = pd.DataFrame(results, columns=column_names)

            # Leer los datos en un DataFrame de pandas
            df = pd.read_sql(query, connection)

            # Calcular el número de valores nulos por fila
            df['null_fields'] = df.isnull().sum(axis=1)

            df.to_csv(OUTPUT_FILE, index=False)

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