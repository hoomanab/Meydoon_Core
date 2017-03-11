# -*- coding: utf8 -*-

import Utilities.Communication.send_sms
from flask_restful import request, Resource
import Config
import Utilities.Communication.send_sms
import Utilities.FileManagement.FileManager
import time


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
                        'shop_id': 0,
                        'Message': "No shop is defined for this user."}
        except Exception as e:
            return {'error': str(e)}

# -*- coding: utf8 -*-

connection = Config.ConnectionManager.MySQLConnection()


class SaveShopInfo(Resource):
    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            _user_id = content['user_id']
            _shop_name = content['shop_name']
            _shop_image = content['shop_image']
            _shop_category_id = content['shop_category_id']
            _shop_verified = False
            _shop_description = content['shop_description']
            _shop_reg_date = time.strftime('%Y-%m-%d %H:%M:%S')
            _shop_product_count = 0
            _shop_followers_count = 0

            # save into database the shop info
            conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.callproc('insertNewShop', (_user_id, _shop_name, _shop_category_id, _shop_description,
                                              _shop_followers_count,_shop_product_count, _shop_reg_date,
                                              _shop_verified))
            data = cursor.fetchone()

            if data[0] > 0:
                # product is saved in the database successfully
                # now save into database the product category info
                conn.commit()
                conn.close()

                conn = connection.opencooncetion()
                cursor = conn.cursor()
                _shop_id = data[0]
                cursor.callproc('saveShopCategory', (_shop_id, _shop_category_id))
                data = cursor.fetchall()

                if len(data) == 0:
                    conn.commit()
                    conn.close()

                    # and finally save product's picture storage address on hard disk
                    storage_address = Utilities.FileManagement.FileManager.Manager.uploadshopfile(_shop_image, _shop_id)

                    conn = connection.opencooncetion()
                    cursor = conn.cursor()
                    cursor.callproc('updateCurrentlyInsertedShop', (storage_address, _shop_id))
                    data = cursor.fetchall()
                    if len(data) == 0:
                        conn.commit()
                        conn.close()
                        return {'error': '0',
                                'StatusCode': '200',
                                'Message': 'shop info completely saved into database successfully.',
                                'shop_id': _shop_id}
                    else:
                        conn.close()
                        # product picture storage address saving encountered an error
                        return {'error': '1',
                                'Message': 'a problem occurred. shop picture storage address'
                                           ' did not inserted into database'}
                else:
                    conn.close()
                    # product category info saving encountered an error
                    return {'error': '1',
                            'Message': 'a problem occurred. shop category info'
                                       ' did not inserted into database'}
            else:
                conn.close()
                # product storage encountered an error
                return {'error': '1',
                        'Message': 'a problem occurred. no shop record inserted into database'}
        except Exception as e:
            return {'error': '0',
                    'Message': 'an exception happened while inserting product info into database.'
                               ' More info is: ' + str(e)}
