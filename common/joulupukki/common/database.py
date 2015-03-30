import sys
import pecan

from pymongo import MongoClient, DESCENDING


try:
    mongo_client = MongoClient(pecan.conf.mongo_server, pecan.conf.mongo_port)
except Exception as exp:
    print(exp)
    sys.exit(1)

mongo = mongo_client[pecan.conf.mongo_db]
