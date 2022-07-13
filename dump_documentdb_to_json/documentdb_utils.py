from multiprocessing.sharedctypes import Value
import pymongo
from pprint import pprint
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from datetime import datetime
import json
import os
import logging
import ssm_util as ssm

DOCUMENT_DB_PASSWORD = "DOCUMENT_DB_PASSWORD"

class DocumentDbUtils:

    def __init__(self, bastion = False) :
        self.bastion = bastion        
        self.client = self.get_db_client()


    def get_db_client(self) :
        vpc = os.environ['VPC']
        password = ""
        if vpc == "true":
            password = ssm.get_secret_from_ssm_in_vpc(DOCUMENT_DB_PASSWORD)
        else:
            password = ssm.get_secret_from_ssm(DOCUMENT_DB_PASSWORD)
            
        dbHost = 'docdb-ds-dev.cluster-cwvakta5mgci.ap-southeast-1.docdb.amazonaws.com'
        
        if self.bastion :
            port = 27117 
            url = 'mongodb://localhost:{}/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'.format(
                port
            ) 
            logging.info(f'bastion using {url}')

            client = pymongo.MongoClient(
                url,
                username='acousticAdmin',
                password = password,
                tls=True,
                tlsAllowInvalidCertificates = True,
                directConnection=True,
                tlsCAFile='rds-combined-ca-bundle.pem'
            )          
        else :
            url = 'mongodb://{}:27017/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'.format(
                dbHost
            ) 

            client = pymongo.MongoClient(
                url,
                username='acousticAdmin',
                password = password,
                tls=True, 
                tlsCAFile='rds-combined-ca-bundle.pem'
            )
        return client


    def set_collection(self, database, collection) :
        db = self.client[database]
        self.collection = db[collection]
        
    def insert(self, doc) :
        insert_result = self.collection.insert_one(doc)
        # print(insert_result)
        return insert_result.inserted_id

    def find_by_id(self, id_str) :
        doc = self.collection.find_one({'_id': ObjectId(id_str)})
        return doc

    def find_one(self, filter = {}) :
        doc = self.collection.find_one(filter) 
        # json_data = dumps(cursor)
        # json_obj = json.loads(json_data)
        return doc

    def delete(self, filter) :
        doc = self.collection.find_one_and_delete(filter)
        return doc

    def close(self) :
        self.client.close()

    def aggregate(self, agg={}) :
        cursor = self.collection.aggregate(agg)
        return list(cursor)
    
    # Hai Tong added the following funciton
    def count(self, filter = {}):
        count = self.collection.count_documents(filter)
        return count

    def find_without_limit(self, filter = {}):
        doc = self.collection.find(filter)
        return doc
        # return list(doc)
    
    def update(self, key, new_value):
        try:
            print("update query: key={}  value={}".format(key, new_value))
            self.collection.update_one(key, new_value)
            return True
        except Exception as e:
            print(e)
        return False
    
    def distinct(self, field, query):
        docs = []
        try:
            docs = self.collection.distinct(field, query)
            return list(docs)
        except Exception as e:
            print(e)
        return list(docs)
    # End of Hai Tong

    def find(self, filter = {}, limit=10) :
        cursor = self.collection.find(filter).limit(limit)
        return list(cursor)

    def get_gte_date_condition(self, dateString, gtFormat = "%Y-%m-%d" ) :
        return {
            '$gte': datetime.strptime(dateString, gtFormat)
        }

    def get_week_from_operator(self, dateField) :
        return {
            "$week": f"${dateField}"
        }

    def get_group_by_count_block(self, keys) :
        obj = {}
        for key in keys :
            obj[key] = f"${key}"
        return {
            "$group": {
                "_id": obj,
                "count": {"$sum": 1}
            }
        }


        
'''
Example Queries 

This query finds exact matches for key value pair
{
    'source': 'Sales'
}

This query finds for a greater than date
        query = {
            'recordDt': {
                '$gt': datetime(2022, 4, 20)
            }
        }


This query finds for less than datestring
        query = {
            'recordDt': {
                '$lt': datetime.strptime("2022-04-20", "%Y-%m-%d")
            }
        }


This aggregation groups by the source field
        {
            "$group": {
                "_id": "$source",
                "counter": {"$sum": 1}
            }
        }

'''
