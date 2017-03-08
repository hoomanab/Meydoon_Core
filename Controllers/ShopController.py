# -*- coding: utf8 -*-

from flask_restful import request, Resource
import Config
import time
from random import randint
import random
import Utilities.Communication.send_sms


connection = Config.ConnectionManager.MySQLConnection()


class GetshopIDbyOwnerID(Resource):

    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            _user_id = content['user_id']

            # retrieve shop_id from database
            conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.callproc('GetshopIDbyOwnerID', (_user_id,))
            data = cursor.fetchall()
            if len(data) > 0:
                conn.commit()
                conn.close()
                return {'error': '0', 'StatusCode': '200', 'shop_id': data[0][0]}
            else:
                # problem in retrieving user id from database
                conn.close()
                return {'error': '0', 'StatusCode': '200',
                        'shop_id': None,
                        'Message': "No shop is defined for this user."}
        except Exception as e:
            return {'error': str(e)}

