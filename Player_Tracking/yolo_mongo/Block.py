#!/usr/bin/env python
# -*- coding: utf-8 -*-



import pandas as pd
from pymongo import MongoClient
import numpy as np
import pickle
url="mongodb+srv://new_user_31:4PoCJvGsGNN3pDuX@cluster0.d6oic.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(url)

mydb = client["yolo-v8"]
collection_list = mydb.list_collections()
for c in collection_list:
    print(c)
collection = mydb["v1"]

collection.drop()

with open("re_dict.pkl", "rb") as tf:
    re_dict = pickle.load(tf)
print(type(re_dict))
for k,v in re_dict.items():
    result = collection.insert_one({k:v})
    print(result.acknowledged)

result = collection.find()
for i in result:
    print(i)
