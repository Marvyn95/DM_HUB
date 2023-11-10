from flask import Flask
from pymongo import MongoClient

#connecting to mongodb database
conn_string = "mongodb://localhost:27017"
dmhub_client = MongoClient(conn_string)

app = Flask(__name__)
app.config["SECRET_KEY"] = "tomriddlemarvolo"

from dm_hub import routes