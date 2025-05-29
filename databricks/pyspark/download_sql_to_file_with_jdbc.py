import os
import csv
import jaydebeapi

def execute_sql_jdbc(query, output_file):
    try:
        driver_class = "com.databricks.client.jdbc.Driver"
        jdbc_url = ""
        # user = ""
        # password = ""
        token = ""

        jars = "/home/callanor/Documents/github/virtual_environments/databricks/pyspark/DatabricksJDBC42.jar"

        if not os.path.exists(jars):
            raise FileNotFoundError(f"El archivo JDBC JAR no se encuentra en: {jars}")

        conn = None
        conn_args = {}
        # if user and password:
        #     conn_args = {
        #         'user':user,
        #         'password':password
        #     }
        conn_args = {
            "PWD": token
        }

        conn = jaydebeapi.connect(
            driver_class,
            jdbc_url,
            conn_args,
            jars
        )

        curs = conn.cursor()
        curs.execute(query)
        results = curs.fetchall()
        column_names = [x[0] for x in curs.description]

        with open(output_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(column_names)
            csv_writer.writerows(results)
        return True

    except Exception as e:
        print(f"Error al ejecutar el query SQL o al guardar el archivo CSV: {e}")
        return False
    finally:
        if conn:
            curs.close()
            conn.close()

def main():
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
    """
    output_file = "output.csv"  # Reemplaza con la ruta donde quieres guardar el archivo CSV

    # Checkear que la variable de ambiente este configurada
    if not os.path.exists("DatabricksJDBC42.jar"):
        print("No se encuentra el archivo DatabricksJDBC42.jar.")
        exit()

    success = execute_sql_jdbc(
        query,
        output_file
    )

    if success:
        print(f"Los resultados del query se han guardado en: {output_file}")
    else:
        print("No se pudieron obtener o guardar los resultados del query.")

if __name__ == "__main__":
    main()