# -*- coding: utf8 -*-

from flask_restful import request, Resource
import Config
import json
from Utilities.DateManager import Manager

connection = Config.ConnectionManager.MySQLConnection()


class GetShopNotifications(Resource):
    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            _user_id = content['user_id']
            _pageNo = content['page_number']
            # this is a constant
            _pageCapacity = 25
            last_index = (_pageCapacity * _pageNo) - 1
            first_index = (last_index - _pageCapacity) + 1
            # get shop notifications to its followers from database
            conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.callproc('GetShopNotificationsforaUser', (_user_id, first_index, _pageCapacity))
            data = cursor.fetchall()
            if len(data) > 0:
                data_as_dict = []

                for row in data:
                    row_as_dict = {
                        'broadcast_message_id': row[0],
                        'shop_table_shop_id': row[1],
                        'broadcast_message_text': row[2],
                        'broadcast_message_date': Manager.datetime_handler(row[3]),
                        'broadcast_message_title': row[4],
                        'follower_user_id': row[5],
                        'followed_shop_id': row[6],
                    }
                    data_as_dict.append(row_as_dict)
                return {'error': '0',
                        'StatusCode': '200',
                        'Feed': json.dumps(data_as_dict)}
            else:
                # no notification is available for current user
                return {'error': '0',
                        'StatusCode': '200',
                        'Message': 'no notification is available for current user'}
        except Exception as e:
            return {'error': '1',
                    'StatusCode': '1000',
                    'Message': 'A problem occured during getting data from database. '
                    'More info is: ' + str(e)}
