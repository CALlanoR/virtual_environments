
from pyspark.sql import SparkSession
from databricks.connect import DatabricksSession
import csv
import os

def execute_sql_query(
        query,
        output_path,
        spark
    ):
    try:
        df = spark.sql(query)
        df.write.csv(
            output_path,
            header=True,
            mode="overwrite") # mode = "overwrite" para sobreescribir si existe
        return True
    except Exception as e:
        print(f"Error al ejecutar el query SQL o al guardar el archivo CSV: {e}")
        return False
    finally:
        if spark is None: # Solo detener la sesion si la función la creo
            spark.stop()

def get_spark_session(app_name):
    # spark = DatabricksSession.builder.remote(app_name) 
    spark = DatabricksSession.builder.remote(serverless=True) \
        .config("spark.databricks.host", "") \
        .config("spark.databricks.client_id", "") \
        .config("spark.databricks.client_secret", "") \
        .getOrCreate()
    return spark

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
    output_path = "/home/callanor/Documents/github/virtual_environments/databricks/pyspark/output.csv" 

    spark = get_spark_session("MiApp")
    success = execute_sql_query(
        query,
        output_path,
        spark
    )

    if success:
        print(f"Los resultados del query se han guardado en: {output_path}")
    else:
        print("No se pudieron obtener o guardar los resultados del query.")
    spark.stop()


if __name__ == "__main__":
    main()