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


class GetRegisteredUserHomeFeed(Resource):
    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            _message = content['message']

            if _message == 'registered_user_home':
                _user_id = content['userId']
                _page_no = content['pageNumber']
                _page_capacity = content['pageCapacity']
                # prepare feed for home page of the guest user
                conn = connection.opencooncetion()
                cursor = conn.cursor()
                cursor.callproc('GetRegisteredUserHomeFeed', (_user_id, _page_no, _page_capacity))
                data = cursor.fetchall()
            if len(data) > 0:
                data_as_dict = []

                for row in data:
                    row_as_dict = {
                        'follower_user_id': row[0],
                        'shop_id': row[1],
                        'shop_name': row[2],
                        'shop_picture_address': row[3],
                        'shop_address': row[4],
                        'shop_phone': row[5],
                        'shop_telegram_id': row[6],
                        'shop_category_id': row[7],
                        'shop_description': row[8],
                        'shop_followers_count': row[9],
                        'shop_product_counter': row[10],
                        'shop_city': row[11],
                        'shop_reg_date': GetGuestUserHomeFeed.datetime_handler(row[12]),
                        'is_verified': row[13],
                        'product_id': row[14],
                        'product_name': row[15],
                        'product_picture_address': row[16],
                        'product_whole_sale_status': row[17],
                        'product_price': str(row[18]),
                        'product_offsale_status': row[19],
                        'product_offsale_price': str(row[20]),
                        'product_shippable_status': row[21],
                        'product_verified_status': row[22],
                        'product_description': row[23],
                        'product_register_date': GetGuestUserHomeFeed.datetime_handler(row[24]),
                        'product_expire_date': GetGuestUserHomeFeed.datetime_handler(row[25]),
                        'product_like_counter': row[26],
                        'product_availability': row[27],
                    }
                    data_as_dict.append(row_as_dict)

                return {'error': '0',
                        'StatusCode': '200',
                        'Feed': json.dumps(data_as_dict)}
            else:
                # problem in getting feed data from database
                return {'error': '1', 'StatusCode': '1000',
                        'Message': 'problem in getting feed data from database'
                        + ' more info is: ' + str(data[0])}

        except Exception as e:
            return {'error': str(e)}
            # return {'StatusCode': '1000', 'Message': str(data[0])}
