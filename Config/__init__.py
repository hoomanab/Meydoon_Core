from flask import Flask
from flask.ext.mysql import MySQL
from flask_restful import Api
from Config import ConnectionManager

app = Flask(__name__)
api = Api(app)
mysql = MySQL()
ConnectionManager.MySQLConnection.setupconnection()
