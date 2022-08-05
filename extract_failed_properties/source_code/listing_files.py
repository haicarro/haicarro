import psycopg2
import json
import boto3 
import os
from datetime import datetime
import time
import audio_engine_utils as engine_utils

def extract_listing_audio_files(event):
    query = '''
        SELECT 
        audio.id,
        audio.inventory_id,
        audio.listing_id,
        audio.inspection_id,
        tmp1.reports,
        audio.inspection_type
        FROM mart_data_science.listing_files_engine_audio audio 
        JOIN 
        (
            SELECT tmp.id, json_agg( tmp.reports::JSON) AS reports
            FROM 
            (
            SELECT id , j ->> 'items' AS reports 
            FROM mart_data_science.listing_files_engine_audio s 
                cross join lateral json_array_elements ( inspection_report::JSON ) AS j
            WHERE {}  j->>'title' IN ('road_test')
            ) AS tmp
            GROUP BY tmp.id
        ) AS tmp1
        ON audio.id = tmp1.id
    '''
    schema = (
         'id', 'inventory_id','listing_id', 'inspection_id', 'inspection_report', 'inspection_type' 
    )
    audio_source = 'listing_files_engine_audio'
    new_path = engine_utils.extract_audio_files(event, query, audio_source, schema)
    return new_path

def lambda_handler(event, context):
    start_time = time.time()
    file_name = extract_listing_audio_files(event)
    end_time = time.time()
    print('Time taken: {} minutes'.format((end_time - start_time)/60))

if __name__ == "__main__":
    # pls provide the following info in case run locally
    os.environ["DB_HOST"] = 'analytics-db-1.cyij8crywzth.ap-southeast-1.rds.amazonaws.com'
    os.environ["DB_PORT"] = '5432'
    os.environ["DB_NAME"] = 'carro_wholesale'
    os.environ["DB_USER"] = 'mart_ds_user_ro'
    os.environ["VPC"] = "true"
    # event = {'from_days_ago': 4}
    event = {'load_method':'all'}
    res = lambda_handler(event, None)
