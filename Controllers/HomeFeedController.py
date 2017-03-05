# -*- coding: utf8 -*-

from flask_restful import request, Resource
import Config
import json

connection = Config.ConnectionManager.MySQLConnection()


class GetGuestUserHomeFeed(Resource):

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
                                'Feed': json.dumps(data, default=lambda o: o),
                                'structure': '[shop_id, shop_name, shop_city, shop_picture, product_id, '
                                              'product_register_date, product_name, product_description, '
                                              'product_picture, product_price'}

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
                        'Message': 'problem in getting feed data from database' +
                                       ' more info is: ' + str(data[0])}
        except Exception as e:
            return {'error': str(e)}
            # return {'StatusCode': '1000', 'Message': str(data[0])}

