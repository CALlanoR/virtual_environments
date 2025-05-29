import datetime
import json
from databricks import sql

server_hostname = ""
http_path = ""
access_token = ""
OUTPUT_FILE = 'output.json'

def row_to_dict(column_names,
                row):
    return dict(zip(column_names, row))

def generate_json_output(cursor):
    column_names = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    json_output =  json.dumps([row_to_dict(column_names, row) for row in rows], default=str) # Convertir a JSON
    return json_output

def generate_paginated_json(page_size,
                            page_number):
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
        offset = (page_number - 1) * page_size 

        query = f"""
            SELECT
                *
            FROM masterfile_reports.report_builder.hcp_reference_report
            LIMIT {page_size}
            OFFSET {offset}
        """ 
        cursor.execute(query)

        json_output = generate_json_output(cursor)

        with open(OUTPUT_FILE, 'w') as outfile:
            outfile.write(json_output)

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

if __name__ == "__main__":
  # Ejemplo de uso:
  page_size = 10
  page_number = 1

  generate_paginated_json(page_size,
                          page_number)