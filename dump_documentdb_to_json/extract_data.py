import os
from pydoc import doc
import documentdb_utils as db
from bson import ObjectId 
import json
from datetime import datetime
import pandas as pd

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.__str__()
        return json.JSONEncoder.default(self, o)

def flatten_inspection_check(docs):
    for d in docs:
        
        if "inspectionChecks" in d:
            ins = d["inspectionChecks"]
            if ins is not None:
                for key, value in ins.items():
                    if value == 1.0:
                        d[key] = "pass"
                    elif value == 0.0:
                        d[key] = "fail"
                    else:
                        d[key] = value
            del d["inspectionChecks"]

        if "metadataFromMediaFile" in d:
            ins = d["metadataFromMediaFile"]
            if ins is not None:
                for key, value in ins.items():
                    d[key] = value
            del d["metadataFromMediaFile"]

    return docs            

def extract_inspection(documentDb, from_date, to_date):
    query = {
        "source": "Inspection",
        }
    if from_date and to_date:
        from_dt = datetime.strptime(from_date,'%Y-%m-%d')
        to_dt = datetime.strptime(to_date,'%Y-%m-%d')
        query = {
            "source": "Inspection",
            "$and": [{"recordDt":{"$gt":from_dt}}, {"recordDt":{"$lt":to_dt}}]
        }

    docs = documentDb.find_without_limit(query)
    docs = list(docs)
    docs = flatten_inspection_check(docs)
    print('Number of records: {}'.format(len(docs)))
    docs = JSONEncoder().encode(docs)
    with open("data/inspection.json", 'w', encoding='utf-8') as f:
      json.dump(json.loads(docs), f, ensure_ascii=False, indent=4)
    
    # convert json to csv using pandas
    df = pd.read_json('data/inspection.json')
    df.drop('_id', inplace=True, axis=1)
    df.drop('__v', inplace=True, axis=1)
    df.drop('_4x4operation', inplace=True, axis=1)
    df = df.reindex(sorted(df.columns), axis=1)
    df.to_csv ('data/inspection.csv', index = None)

def extract_sales(documentDb, from_date, to_date):
    query = {
        "source": "Sales",
        }
    if from_date and to_date:
        from_dt = datetime.strptime(from_date,'%Y-%m-%d')
        to_dt = datetime.strptime(to_date,'%Y-%m-%d')
        query = {
            "source": "Sales",
            "$and": [{"recordDt":{"$gt":from_dt}}, {"recordDt":{"$lt":to_dt}}]
        }
    docs = documentDb.find_without_limit(query)
    docs = list(docs)
    docs = flatten_inspection_check(docs)
    print('Number of records: {}'.format(len(docs)))
    docs = JSONEncoder().encode(docs)
    with open("data/listing.json", 'w', encoding='utf-8') as f:
      json.dump(json.loads(docs), f, ensure_ascii=False, indent=4)
    
    # convert json to csv using pandas
    df = pd.read_json('data/listing.json')
    df.drop('_id', inplace=True, axis=1)
    df.drop('__v', inplace=True, axis=1)
    df.drop('_4x4operation', inplace=True, axis=1)
    df = df.reindex(sorted(df.columns), axis=1)
    df.insert(len(df.columns)-1, 'listingId', df.pop('listingId'))
    df.to_csv ('data/listing.csv', index = None)

def extract_workshop(documentDb, from_date, to_date):
    query = {
        "source": "Workshop",
        }
    if from_date and to_date:
        from_dt = datetime.strptime(from_date,'%Y-%m-%d')
        to_dt = datetime.strptime(to_date,'%Y-%m-%d')
        query = {
            "source": "Workshop",
            "$and": [{"recordDt":{"$gt":from_dt}}, {"recordDt":{"$lt":to_dt}}]
        }

    docs = documentDb.find_without_limit(query)
    docs = list(docs)
    docs = flatten_inspection_check(docs)
    print('Number of records: {}'.format(len(docs)))
    docs = JSONEncoder().encode(docs)
    with open("data/carro_sound.json", 'w', encoding='utf-8') as f:
      json.dump(json.loads(docs), f, ensure_ascii=False, indent=4)

    #convert json to csv using pandas
    df = pd.read_json('data/carro_sound.json')
    df.drop('_id', inplace=True, axis=1)
    df.drop('__v', inplace=True, axis=1)

    df = df.reindex(sorted(df.columns), axis=1)

    df.to_csv ('data/carro_sound.csv', index = None)


if __name__ == "__main__":
    os.environ["VPC"] = "true"
    documentDb = db.DocumentDbUtils(bastion=True)
    documentDb.set_collection(database='test', collection='sounds')
    #extract_workshop(documentDb, "2022-07-10", "2022-08-04")
    # extract_sales(documentDb, "", "")
    extract_inspection(documentDb, "", "")
