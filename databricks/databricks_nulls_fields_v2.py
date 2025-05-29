
from collections import OrderedDict
from databricks import sql
import json
import os

SERVER_HOSTNAME = ""
HTTP_PATH = ""
ACCESS_TOKEN = ""
DATABASE_NAME = "masterfile_reports.report_builder"
TABLE_NAME = "hco_contacts_report"
COLUMN_KEY = "hco_contacts_id"
OUTPUT_CSV = TABLE_NAME + "null_counts.csv"
CHUNK_SIZE = 1000000

def count_nulls_in_chunks(server_hostname, 
                          http_path, 
                          access_token, 
                          database_name, 
                          table_name, 
                          output_csv, 
                          chunk_size=10000):
    """
    Counts null values per row in a Databricks table, processing in chunks to prevent OOM errors.

    Args:
        server_hostname: Databricks server hostname.
        http_path: Databricks HTTP path.
        access_token: Databricks access token.
        database_name: Name of the database.
        table_name: Name of the table.
        output_csv: Path to the output CSV file.
        chunk_size: Number of rows to process in each chunk.  Adjust based on your cluster size and data width.
    """

    try:
        with sql.connect(server_hostname=server_hostname,
                         http_path=http_path,
                         access_token=access_token) as connection:
            
            print("Connection established with Databricks...")

            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {database_name}.{table_name} LIMIT 1")
                column_names = [desc[0] for desc in cursor.description]

                print("Executing first query to get all column names...")

            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {database_name}.{table_name}")
                total_rows = cursor.fetchone()[0]

                print(f"Total rows in the table {TABLE_NAME} is {str(total_rows)}")

            offset = 0
            summary_null_count = {}

            while offset < total_rows:
                sql_query = f"""
                    SELECT
                        {COLUMN_KEY},
                        (
                            {' + '.join(f'CASE WHEN `{col}` IS NULL THEN 1 ELSE 0 END' for col in column_names)}
                        ) AS null_count
                    FROM
                        {database_name}.{table_name}
                    LIMIT {chunk_size}
                    OFFSET {offset}
                """

                print(f"query: {sql_query}\n")
                start_time = os.times().elapsed 

                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    results = cursor.fetchall()

                    for row in results:
                        null_count = int(row.null_count)

                        if null_count in summary_null_count:
                            summary_null_count[null_count] += 1
                        else:
                            summary_null_count[null_count] = 1

                    query_time = os.times().elapsed - start_time 

                print(f"Executed query, processing data. Time={query_time}")
                start_time = os.times().elapsed

                data_processing_time = os.times().elapsed - start_time

                print(f"Data Processing Time: {data_processing_time}")

                offset += chunk_size

            print(json.dumps(summary_null_count, sort_keys=True, indent=4))

    except sql.Error as e:
        print(f"SQL Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    count_nulls_in_chunks(SERVER_HOSTNAME,
                          HTTP_PATH,
                          ACCESS_TOKEN,
                          DATABASE_NAME,
                          TABLE_NAME,
                          OUTPUT_CSV,
                          CHUNK_SIZE)
    

# hco
# TotalRows: 6.313.085
# totalFields: 52
# {
#     "4": 724,
#     "5": 6656,
#     "6": 32416,
#     "7": 328813,
#     "8": 594542,
#     "9": 330767,
#     "10": 187589,
#     "11": 81822,
#     "12": 437622,
#     "13": 399746,
#     "14": 291434,
#     "15": 139554,
#     "16": 90349,
#     "17": 147481,
#     "18": 1844929,
#     "19": 678177,
#     "20": 219004,
#     "21": 50372,
#     "22": 10747,
#     "23": 11289,
#     "24": 398922,
#     "25": 3749,
#     "26": 18440,
#     "27": 1282,
#     "28": 922,
#     "29": 177,
#     "30": 241,
#     "31": 236,
#     "32": 3310,
#     "33": 301,
#     "34": 12,
#     "36": 451,
#     "37": 998,
#     "38": 8,
#     "44": 3
# }

# hcp
# totalFields: 51
# TotalRows: 31.375.653
# {
#     "1": 2411,
#     "2": 702898,
#     "3": 518606,
#     "4": 173008,
#     "5": 512711,
#     "6": 1493839,
#     "7": 1368531,
#     "8": 630057,
#     "9": 1317793,
#     "10": 1360647,
#     "11": 1042944,
#     "12": 945499,
#     "13": 1691206,
#     "14": 2184493,
#     "15": 1230503,
#     "16": 1577437,
#     "17": 2373749,
#     "18": 2897192,
#     "19": 1940861,
#     "20": 1324781,
#     "21": 3192857,
#     "22": 2518002,
#     "23": 263395,
#     "24": 89348,
#     "25": 6633,
#     "26": 4344,
#     "27": 2646,
#     "28": 1086,
#     "29": 761,
#     "30": 518,
#     "31": 312,
#     "32": 31,
#     "33": 58,
#     "34": 4767,
#     "35": 1485,
#     "36": 98,
#     "37": 27,
#     "38": 25,
#     "39": 25,
#     "40": 69
# }

# prescribing_authority_report
# totalFields: 16
# TotalRows: 2.071.536
# {
#     "1": 1573929,
#     "2": 393737,
#     "3": 1385,
#     "6": 69,
#     "7": 163,
#     "8": 95287,
#     "10": 6966
# }

# hco_contacts_report
# totalFields: 30
# TotalRows: 2.710.205
# {
#     "1": 345,
#     "2": 1208675,
#     "3": 209308,
#     "4": 97,
#     "5": 105048,
#     "6": 551521,
#     "7": 2274,
#     "8": 80317,
#     "9": 546372,
#     "10": 275,
#     "11": 4690,
#     "12": 441,
#     "13": 140,
#     "14": 638,
#     "15": 54,
#     "16": 10
# }