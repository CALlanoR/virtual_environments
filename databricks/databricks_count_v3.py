
from databricks import sql
import pandas as pd
import os

SERVER_HOSTNAME = ""
HTTP_PATH = ""
ACCESS_TOKEN = ""
DATABASE_NAME = "masterfile_reports.report_builder"
TABLE_NAME = "hco_contacts_report"


def main(server_hostname, 
         http_path, 
         access_token, 
         database_name, 
         table_name):

    try:
        with sql.connect(server_hostname=server_hostname,
                         http_path=http_path,
                         access_token=access_token) as connection:
            
            print("Connection established with Databricks...")

            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {database_name}.{table_name}")
                total_rows = cursor.fetchone()[0]

                print(f"Total rows in the table {TABLE_NAME} is {str(total_rows)}")

    except sql.Error as e:
        print(f"SQL Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main(SERVER_HOSTNAME,
         HTTP_PATH,
         ACCESS_TOKEN,
         DATABASE_NAME,
         TABLE_NAME)