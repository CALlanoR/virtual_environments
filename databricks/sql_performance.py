from databricks import sql
import os
from datetime import datetime
import pickle
import pandas as pd

def measure_databricks_sql_performance(query: str):
    start_time = datetime.now()
    try:
        with sql.connect(
            server_hostname = "",
            http_path       = "",
            access_token    = ""
            ) as connection:
           
            with connection.cursor() as cursor:
                execution_start = datetime.now()
                # cursor.execute(disable_cached_results_str)
                cursor.execute(query)
                execution_end = datetime.now()
                print("antes de fetchall")
                data=cursor.fetchall()
                print("despues de fetchall")
                fetch_end = datetime.now()
                
                df = pd.DataFrame(data) 
                serialized_df = pickle.dumps(df)
                data_size_bytes = len(serialized_df)
                data_size_mb = data_size_bytes / (1024 ** 2)
      
        timings = {
            'result_size_mb': data_size_mb,
            'connection_time': (execution_start - start_time).total_seconds(),
            'execution_time': (execution_end - execution_start).total_seconds(),
            'fetch_time': (fetch_end - execution_end).total_seconds(),
            'total_time': (fetch_end - start_time).total_seconds()
        }
        return timings
    except Exception as e:
        print(f"Error in Databricks SQL performance measurement: {e}")
        return None

if __name__ == "__main__":   
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
        LIMIT 1000000
    """
    print(measure_databricks_sql_performance(query))
