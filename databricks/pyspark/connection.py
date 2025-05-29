import jaydebeapi
import pandas as pd

# Databricks JDBC connection parameters

JDBC_URL = ""
JDBC_DRIVER_PATH = "/home/callanor/Documents/github/virtual_environments/databricks/pyspark/DatabricksJDBC42.jar"
JDBC_DRIVER_CLASS = "com.databricks.client.jdbc.Driver"
QUERY = "SELECT * FROM report_builder.hcp_reference_report  LIMIT 100"
OUTPUT_CSV = "output.csv"

# Connect to Databricks using JDBC
def connect_to_databricks():
    conn = jaydebeapi.connect(JDBC_DRIVER_CLASS, JDBC_URL, ["", ""], JDBC_DRIVER_PATH)
    return conn

# Execute query and write results to CSV
def execute_query_and_write_csv():
    conn = connect_to_databricks()
    try:
        cursor = conn.cursor()
        cursor.execute(QUERY)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"Data written to {OUTPUT_CSV}")
    finally:
        conn.close()

if __name__ == "__main__":
    execute_query_and_write_csv()

