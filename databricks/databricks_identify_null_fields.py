from databricks import sql
import pandas as pd

SERVER_HOSTNAME = ""
HTTP_PATH = ""
ACCESS_TOKEN = ""
CATALOG = "masterfile_reports"
SCHEMA = "report_builder"
TABLE_NAME = "hcp_reference_report"

def main(server_hostname,
         http_path,
         access_token,
         catalog,
         schema,
         table_name,
         csv_file_path):
    """
    Counts and identifies fields with null values in a Databricks SQL table.

    Args:
        server_hostname: Databricks server hostname.
        http_path: Databricks HTTP path.
        access_token: Databricks access token.
        catalog (str): Name of the catalog
        schema (str): Name of the schema.
        table_name: Name of the table.

    Returns:
        pandas.DataFrame: A DataFrame with the column name and the null value count.

    Returns None if there is an error.
    """

    try:
        with sql.connect(server_hostname=server_hostname,
                         http_path=http_path,
                         access_token=access_token) as connection:

            with connection.cursor() as cursor:
                cursor.execute(f"USE CATALOG `{catalog}`")
                cursor.execute(f"USE SCHEMA `{schema}`")
                cursor.execute(f"DESCRIBE TABLE `{table_name}`")
                schema_info = cursor.fetchall()

                null_counts = []
                for col in schema_info:
                    column_name = col[0]

                    query = f"""
                        SELECT COUNT(*) FROM `{table_name}`
                        WHERE `{column_name}` IS NULL
                    """
                    cursor.execute(query)
                    null_count = cursor.fetchone()[0]
                    null_counts.append((column_name, null_count))

        df_nulls = pd.DataFrame(null_counts, columns=['Column Name', 'Null Count'])
        df_nulls = df_nulls[df_nulls['Null Count'] > 0] # Filter only columns with null values.
        df_nulls.sort_values(by='Null Count', ascending=False).reset_index(drop=True)

        df_nulls.to_csv(csv_file_path, index=False)  # index=False evita que se escriba el índice del DataFrame

        return csv_file_path

    except Exception as e:
        print(f"Error: {e}")
        return None


csv_path = main(SERVER_HOSTNAME,
                HTTP_PATH,
                ACCESS_TOKEN,
                CATALOG,
                SCHEMA,
                TABLE_NAME,
                CATALOG + "_" + SCHEMA + "_" + TABLE_NAME + ".csv")

if csv_path is not None:
    print(f"El conteo de valores nulos se ha guardado en: {csv_path}")
else:
    print("Ocurrió un error al ejecutar la función.")