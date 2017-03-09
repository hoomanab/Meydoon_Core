# -*- coding: utf8 -*-

import datetime
from flask_restful import request, Resource
import Config
import json

connection = Config.ConnectionManager.MySQLConnection()


class GetGuestUserHomeFeed(Resource):

    @staticmethod
    def datetime_handler(x):
        if x is None:
            return None
        if isinstance(x, datetime.datetime):
            return x.isoformat()
        raise TypeError("Unknown type")

    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            _message = content['Message']

            if _message == 'guest home':
                _pageNo = content['pageNumber']
                _pageCapacity = content['pageCapacity']
                # prepare feed for home page of the guest user
                conn = connection.opencooncetion()
                cursor = conn.cursor()
                cursor.callproc('GetGuestUserHomeFeed', (_pageNo, _pageCapacity))
            data = cursor.fetchall()
            if len(data) > 0:
                data_as_dict = []

                for row in data:
                    row_as_dict = {
                        'shop_id': row[0],
                        'shop_name': row[1],
                        'shop_city': row[2],
                        'shop_picture_address': row[3],
                        'product_id': row[4],
                        'product_register_date': GetGuestUserHomeFeed.datetime_handler(row[5]),
                        'product_name': row[6],
                        'product_description': row[7],
                        'product_picture_address': row[8],
                        'product_price': str(row[9]),
                    }
                    data_as_dict.append(row_as_dict)

                return {'error': '0',
                        'StatusCode': '200',
                        'Feed': json.dumps(data_as_dict)}

            else:
                # problem in getting feed data from database
                return {'error': '1', 'StatusCode': '1000',
                        'Message': 'problem in getting feed data from database' +
                                       ' more info is: ' + str(data[0])}
        except Exception as e:
            return {'error': str(e)}
            # return {'StatusCode': '1000', 'Message': str(data[0])}


class GetAuthenticatedUserHomeFeed(Resource):

    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            _message = content['Message']

            if _message == 'guest home':
                _pageNo = content['pageNumber']
                _pageCapacity = content['pageCapacity']
                # prepare feed for home page of the guest user
                conn = connection.opencooncetion()
                cursor = conn.cursor()
                cursor.callproc('GetGuestUserHomeFeed', (_pageNo, _pageCapacity))
            data = cursor.fetchall()
            if len(data) > 0:

                return {'error': '0', 'StatusCode': '200',
                        'Feed': data}
            else:
                # problem in getting feed data from database
                return {'error': '1', 'StatusCode': '1000',
                        'Message': 'problem in getting feed data from database'
                        + ' more info is: ' + str(data[0])}

        except Exception as e:
            return {'error': str(e)}
            # return {'StatusCode': '1000', 'Message': str(data[0])}
