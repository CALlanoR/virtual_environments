import datetime
from databricks import sql

server_hostname = ""
http_path = ""
access_token = ""

try:
    start = datetime.datetime.now()
    print("------------- start --------------")
    print(str(start) + "")

    connection = sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        access_token=access_token
    )

    print("Conexión establecida con Databricks.")

    with connection.cursor() as cursor:
        query = "SELECT hcp_pl_id, hcp_overview_first FROM masterfile_reports.report_builder.hcp_reference_report WHERE hcp_pl_id = 28"
        # query = "SELECT hco_overview_name  FROM masterfile_reports.report_builder.hco_reference_report LIMIT 1000"
        # query = "SELECT * FROM masterfile_reports.report_builder.hcp_reference_report LIMIT 1000000"
        cursor.execute(query)

        for row in cursor.fetchall():
            print(row)
            # print(f"Resultado: {row['hcp_identifiers_id_type_description']}")

    end = datetime.datetime.now()
    print("--------------------------------------")
    print(str(end))
    elapsed = end - start
    print("elapsed seconds: " + str(elapsed) + "")
    print("--------------- end -------------------")

except Exception as e:
    print(f"Error al conectarse o ejecutar el query: {e}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("Conexión cerrada.")
