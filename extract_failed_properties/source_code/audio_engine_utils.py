from pickle import NONE
from re import I
import boto3
import os
import json
import psycopg2
from datetime import datetime, timedelta
import ssm_util as ssm
import pandas as pd
# from bson import json_util

DATAMART_PASSWORD = "DATAMART_PASSWORD"
note_inspections = ["engine_starts_properly", "engine_idles_properly", "engine_noise"]
def extract_engine_information(inspection_array):
    for inspection_ele in inspection_array:
        ins_reports = inspection_ele['inspection_report']
        if ins_reports is not None:
            for ins in ins_reports:
                for ins1 in ins:
                    name = ins1['name']
                    # inspection_ele[name] = ins1['status']
                    # note inspection
                    if (name in note_inspections) and (ins1['status'] in ['fail']):
                        inspection_ele[name] = ins1['status']
                        if "notes_value" in ins1:
                            notes_value = ins1['notes_value']
                            if (notes_value is not None) and ("remarks" in notes_value):
                                remarks = notes_value['remarks']
                                inspection_ele[name + "_notes"] = remarks
        del inspection_ele['inspection_report']

    new_inspection_array = []
    for ins in inspection_array:
        if ("engine_starts_properly" in ins) or ("engine_idles_properly" in ins) or ("engine_noise" in ins):
            new_inspection_array.append(ins)

    return new_inspection_array

def extract_audio_files(event, query, audio_source, schema):
    s_host = os.environ['DB_HOST']
    s_port =os.environ['DB_PORT']
    s_dbname =os.environ['DB_NAME']
    s_name_user =os.environ['DB_USER']
    s_vpc = os.environ['VPC']
    s_password = ""
    if s_vpc == "true":
        # lambda was deployed in VPC
        s_password = ssm.get_secret_from_ssm_in_vpc(DATAMART_PASSWORD)
    else:
        # lambda is outside VPC
        s_password = ssm.get_secret_from_ssm(DATAMART_PASSWORD)

    db_conn_source = psycopg2.connect(host=s_host, port=s_port, dbname=s_dbname, user=s_name_user, password=s_password)
    db_cursor_source = db_conn_source.cursor()
    load_method = event.get('load_method', 'incremental')
    if load_method != 'all':
        from_days_ago = event['from_days_ago']
        expected_time = datetime.today() - timedelta(days=from_days_ago)
        expected_time = expected_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        where_condition = 'file_created_at > \'{}\' AND '.format(expected_time)
        query = query.format(where_condition)
    else:
        query = query.replace("{}", "")
    print(query)
    
    db_cursor_source.execute(query)
    json_audio = []
    for row in db_cursor_source.fetchall():
        json_audio.append(dict(zip(schema, row)))
    db_cursor_source.close()
    db_conn_source.close()

    if json_audio is not None:
        json_audio = extract_engine_information(json_audio)
        print("Number of new audio files: {}".format(len(json_audio)))
    else:
        json_audio = []

    # Make a directory
    working_folder = "data"
    file_name = '{}.json'.format(audio_source)
    if not os.path.exists(os.path.join(working_folder)):
        os.makedirs(working_folder)
    save_path = os.path.join(working_folder, file_name)
    
    with open(save_path, 'w', encoding='utf-8') as f:
      json.dump(json_audio, f, ensure_ascii=False, indent=4, default=str)

    df = pd.read_json(save_path)
    new_save_path = save_path.replace(".json", ".csv")
    df.to_csv (new_save_path, index = None)

    return save_path
