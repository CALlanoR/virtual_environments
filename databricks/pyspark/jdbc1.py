from pyspark.sql import SparkSession
from databricks.connect import DatabricksSession
import os

def get_jdbc_spark_session(app_name="MiAplicacionSpark"):
    """
    Crea y retorna una SparkSession configurada para conectarse a Databricks
    a través de JDBC.
    """
    # Cargar la configuración desde variables de entorno
    jdbc_url = ""
    driver_class = "com.databricks.client.jdbc.Driver"
    jdbc_jar_path = "/home/callanor/Documents/github/virtual_environments/databricks/pyspark/DatabricksJDBC42.jar"

    user = ""
    password = ""
    token = ""

    if not jdbc_url or not jdbc_jar_path:
        raise ValueError("Las variables de entorno DATABRICKS_JDBC_URL y DATABRICKS_JDBC_JAR_PATH deben estar definidas.")

    if not os.path.exists(jdbc_jar_path):
        raise FileNotFoundError(f"El archivo JDBC JAR no se encuentra en: {jdbc_jar_path}")

    # Configurar la SparkSession
    spark = DatabricksSession.builder.appName(app_name)
    spark = spark.config("spark.databricks.host", "")
    spark = spark.config("spark.driver.extraClassPath", jdbc_jar_path) \
    spark = spark.config("spark.jars", jdbc_jar_path) # Esto es para el driver
        #.config("spark.driver.user", user) \
        #.config("spark.driver.password", password) # En caso de usar usuario y password
    #Configurar las credenciales en caso de existir

    if user and password:
        spark = spark.config("spark.driver.user", user)
        spark = spark.config("spark.driver.password", password)
    elif token:
        spark = spark.config("spark.driver.user", "token")
        spark = spark.config("spark.driver.password", token)

    spark = spark.config("javax.jdo.option.ConnectionURL", jdbc_url) \
            .config("javax.jdo.option.ConnectionDriverName", "com.databricks.client.jdbc.Driver")
    spark = spark.getOrCreate()
    print ("Conectado mediante JDBC, recuerda tener el host y la base de datos en el string")
    return spark

def execute_sql_and_save_to_csv(spark, query, output_path):
    """
    Ejecuta un query SQL en Databricks usando la SparkSession proporcionada
    y guarda el resultado en un archivo CSV.  Ya no usa la librería jaydebeapi!
    """
    try:
        # Leer la tabla usando JDBC
        df = spark.read.format("jdbc") \
        .option("url", "") \
        .option("driver", "com.databricks.client.jdbc.Driver") \
        .option("dbtable", f"({query}) as tmp") \
        .option("user", "" or 'token')  \
        .option("password", "" or "")  \
        .load()


        # Escribir el DataFrame a CSV
        df.write.csv(output_path, header=True, mode="overwrite")
        return True
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return False

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
    output_path = "output.csv"

    try:

        # 1. Crea la SparkSession configurada para JDBC
        spark = get_jdbc_spark_session()

        # 2. Ejecuta el query y guarda a CSV
        success = execute_sql_and_save_to_csv(spark, query, output_path)

        if success:
            print(f"Los resultados se han guardado exitosamente en {output_path}")
        else:
            print("Hubo un problema al ejecutar el query o guardar los resultados.")

    except Exception as e:
        print(f"Ocurrió un error en el main: {e}")

    finally:
         if 'spark' in locals():  # Check if spark is defined before stopping
             spark.stop()

if __name__ == "__main__":
    main()