import datetime
import csv
from databricks import sql
import pandas as pd

server_hostname = ""
http_path = ""
access_token = ""


try:
    start_execution = datetime.datetime.now()
    print(f"start_execution: {start_execution}")

    with sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        access_token=access_token
    ) as connection:

        print("Conexión establecida con Databricks.")

        with connection.cursor() as cursor:
            query = """
                SELECT
                    DISTINCT
                    hcp_overview_npi
                    , hcp_overview_first
                    , hcp_overview_middle
                    , hcp_overview_last
                    , hcp_overview_profession
                    , hcp_overview_taxonomy_code
                    , hcp_overview_taxonomy_description
                    , hcp_overview_gender
                    , hcp_overview_years_in_practice
                    , hcp_overview_loc_pl_id
                    , hcp_overview_phone
                    , hcp_overview_address1
                    , hcp_overview_address2
                    , hcp_overview_city
                    , hcp_overview_state
                    , hcp_overview_zip5
                    , hcp_overview_county
                    , hcp_overview_division
                    , hcp_overview_region
                    , hcp_overview_cbsa_code
                    , hcp_overview_cbsa_description
                    , hcp_overview_latitude
                    , hcp_overview_longitude
                    , hcp_overview_geo_precision
                    , hcp_overview_status
                    , hcp_overview_status_date
                    , hcp_overview_last_updated_date
                    , hcp_pl_id
                    , hcp_identifiers_id_type_code
                    , hcp_identifiers_id_type_description
                    , hcp_identifiers_id_value
                    , hcp_identifiers_id_issuing_state
                    , hcp_identifiers_id_issuing_auth_license_type
                    , hcp_identifiers_id_status
                    , hcp_identifiers_id_issue_date
                    , hcp_identifiers_id_expiration_date
                    , hcp_identifiers_last_updated_date
                    , hcp_languages_language_code
                    , hcp_languages_language_description
                    , hcp_languages_last_updated_date
                    , hcp_online_presence_url_type_code
                    , hcp_online_presence_url_type_description
                    , hcp_online_presence_url
                    , hcp_online_presence_last_updated_date
                    , hcp_email_email_type_code
                    , hcp_email_email_type_description
                    , hcp_email_email
                    , hcp_email_is_preferred
                    , hcp_email_status
                    , hcp_email_status_date
                FROM masterfile_reports_prod.report_builder.hcp_reference_report
                LIMIT 20000000
            """
            cursor.execute(query)

            start_fetchall = datetime.datetime.now()
            print(f"start_fetchall: {start_fetchall}")
            results = cursor.fetchall()
            end_fetchall = datetime.datetime.now()
            print(f"end_fetchall: {end_fetchall}")

            # print(results)

    end_execution = datetime.datetime.now()
    print(f"end_execution: {end_execution}")
          
    print("--------------- summary -------------------")
    elapsed_execution = end_execution - start_execution
    elapsed_fetchall = end_fetchall - start_fetchall
    print("elapsed seconds execution: " + str(elapsed_execution))
    print("elapsed seconds fetchall: " + str(elapsed_fetchall))
    print("--------------- end -------------------")

except Exception as e:
    print(f"Error al conectarse o ejecutar el query: {e}")

finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("Conexión cerrada.")