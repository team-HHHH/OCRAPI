import os
import re

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import (TypeVar, Optional)
from dotenv import load_dotenv
import bson
import pymongo

ID_PASSWD_FILE = "password"
class MongoDB:
    def __init__(self):
        self.uri = ""
        self.uri2 = ""
        self.get_url()
        self.err = False
        try:
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            self.client2 = MongoClient(self.uri2, server_api=ServerApi("1"))
        except pymongo.errors.ConnectionFailure:
            self.err = True

    def get_url(self):
        load_dotenv()
        self.uri = f"mongodb+srv://{os.environ.get('ID')}:{os.environ.get('PASSWORD')}@dodream.cmvgh.mongodb.net/?retryWrites=true&w=majority&appName=Dodream"
        self.uri2 = f"mongodb+srv://{os.environ.get('ID')}:{os.environ.get('PASSWORD')}@dodream.cmvgh.mongodb.net/?retryWrites=true&w=majority&appName=Dodream"

    def insert(self, dbName:"str", tableName:"str", queryList: list, primaryKey="", primaryKeySet=False, client = None):
        ''' MongoDB의 dbName.tableName 에 insert를 하는 메소드
         _ Junhyeong (20190511)
        :param dbName: Database Name
        :param tableName: table Name
        :param queryList: query List
        :param primaryKey: PK 설정 시 index 이름
        :param primaryKeySet: PK 설정여부
        :return: 성공 시 True 에러시 False
        :return:
        '''
        if client is None:
            client = self.client
        db = client[dbName]
        collections = db[tableName]

        if primaryKeySet:
            for queryDict in queryList:
                queryDict["_id"] = queryDict[primaryKey]

        try:
            collections.insert_many(queryList)
        except pymongo.errors.BulkWriteError:
            return self.insert_listone(dbName, tableName, queryList, primaryKey, primaryKeySet)
        except TypeError:
            return False
        return True

    def insert_listone(self, dbName:"str", tableName:"str", queryList: list, primaryKey="", primaryKeySet=False, client=None):
        ''' Primary Key 충돌로 인하여 한 Query 씩 Insert 할 시 돌아가는 System Method
         _ Junhyeong (20190511)
        :param dbName: Database Name
        :param tableName: table Name
        :param queryList: query List
        :param primaryKey: PK 설정 시 index 이름
        :param primaryKeySet: PK 설정여부
        :return: 성공 시 True 에러시 False
        '''
        if client is None:
            client = self.client
        db = client[dbName]
        collections = db[tableName]

        if primaryKeySet:
            for queryDict in queryList:
                queryDict["_id"] = queryDict[primaryKey]

        #print(queryList)
        for item in queryList:
            try:
                collections.insert_one(item)
            except pymongo.errors.DuplicateKeyError:
                print(f"key:{item} 이미 존재 하므로 pass ...")
                continue
            except Exception:
                print(f"Key:{item} 알 수 없는 에러..")
                return False

        return True


    def read(self, dbname: str, tablename: str, query={}, client=None) -> list:
        ''' MongoDB 에서 dbName.tablename 에 해당하는 모든 Record 를 dictionary List 형태로 반환
        _ Junhyeong (20190511)
        :param dbname: database name 
        :param tablename: table name
        :return: 해당 table의 딕셔너리가 들어있는 리스트
        '''
        if client is None:
            client = self.client
        db = client[dbname]
        collections = db[tablename]
        rawDict = collections.find(query)
        retDict = [{k: v for k, v in d.items() if k != "_id"} for d in rawDict]
        return retDict

    def read_first_one(self, dbname: str, tablename: str, idx="", query={}, limits=1, client=None) -> dict:
        ''' MongoDB 에서 dbName.tableName 에 해당 하는 가장 첫 번째 record 반환
         _ Junhyeong (20190511)
        :param dbname: Database Name
        :param tablename: Table Name
        :param idx: 정렬시킬 인덱스
        :parm query: 찾을 쿼리
        :return: 해당 하는 dictionary 값
        '''
        if idx == "":
            idx = "_id"

        if client is None:
            client = self.client
        db = client[dbname]
        collections = db[tablename]

        if limits == 1:
            return collections.find_one(query, sort=[(idx, pymongo.ASCENDING)])
        else:
            return collections.find(query, sort=[(idx, pymongo.ASCENDING)]).limit(limits)

    def read_last_one(self, dbname: str, tablename: str, idx="", query={}, limits=1, client=None) -> dict:
        ''' MongoDB 에서 dbName.tableName 에 해당 하는 가장 마지막 record 반환
         _ Junhyeong (20190511)
        :param dbname: Database Name
        :param tablename: Table Name
        :return: 해당하는 dictionary 값
        '''
        if idx == "":
            idx = "_id"
        if client is None:
            client = self.client
        db = client[dbname]
        collections = db[tablename]

        if limits == 1:
            return collections.find_one(query, sort=[(idx, pymongo.DESCENDING)])
        else:
            return collections.find(query, sort=[(idx, pymongo.DESCENDING)]).limit(limits)

    def read_list_obj(self, dbname: str, tablename: str, idx="", query={}, client=None) -> Optional[bson.typings._DocumentType]:
        if idx == "":
            idx = "_id"
        if client is None:
            client = self.client

        db = client[dbname]
        collections = db[tablename]
        return collections.find_one(query)

    ####################
    ## Utility

    def string_converter(self, str):
        if str is None:
            return ""
        return re.escape(str)

    def insert_poster_query(self, query):
        query['_id'] = query['id']
        db = self.client["Dodream"]
        collections = db['posterInfo']

        try:
            collections.insert_one(query)
        except pymongo.errors.DuplicateKeyError:
            print(f"key:{query} 이미 존재 하므로 pass ...")
            return False
        except Exception:
            print(f"Key:{query} 알 수 없는 에러..")
            return False

        return True

    def replace_one(self, dbName:"str", tableName:"str", origin_query:dict, query: list, primaryKey="", primaryKeySet=False, client=None):
        if client is None:
            client = self.client

        if primaryKeySet:
            query['_id'] = query[primaryKey]

        db = client[dbName]
        collections = db[tableName]

        try:
            collections.replace_one(origin_query, query)
        except pymongo.errors.DuplicateKeyError:
            print(f"key:{query} 이미 존재 하므로 pass ...")
            return False
        except Exception as e:
            print(f"Key:{query} 알 수 없는 에러..{str(e)}")
            return False

        return True


    def ___create_location_index___(self, db="Dodream", table="posterInfo"):
        client = self.client
        db = client[db]
        collection = db[table]

        indexes = collection.index_information()
        for idx_name, idx_info in indexes.items():
            if "2dsphere" in idx_name:
                print(f"{idx_info['key']} 가 이미 존재함.. ")
                return

        collection.create_index([("uPos", "2dsphere")])
        collection.create_index([("pPos", "2dsphere")])


if __name__ == "__main__":
    obj = MongoDB()
    #obj.___create_location_index___()
    #print(obj.read_seller_list())
    #print(obj.insert(dbName="Hospital", tableName="naverinfo", queryList=[{"name": "예시"}]))

    #data = obj.read_hospital_code("강남편안한치과의원")
    # DB에 들어가는지 확인..
    #print(obj.read_list_obj("DayInfo", "Info", "", ))
    #print(obj.read("StockCode", "KOSPI",  {"company": "동화약품"}))
