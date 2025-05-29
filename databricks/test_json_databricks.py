import datetime
import json
from databricks import sql

server_hostname = ""
http_path = ""
access_token = ""

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
        # query = "SELECT hco_overview_name,  FROM masterfile_reports.report_builder.hco_reference_report LIMIT 1000"
        query = "SELECT * FROM masterfile_reports.report_builder.hcp_reference_report"
        cursor.execute(query)

        column_names = [desc[0] for desc in cursor.description]

        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(column_names, row)))

    json_output = json.dumps(results, indent=4, default=str) # el default=str es para los datetime que no se serializean

    print(json_output)

    # with open('output.json', 'w') as outfile:
    #     outfile.write(json_output)
    # print("JSON guardado en output.json")


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