# -*- coding: utf8 -*-

import Utilities.Communication.send_sms
from Utilities.DateManager import Manager
from flask_restful import request, Resource
import Config
import Utilities.Communication.send_sms
import Utilities.FileManagement.FileManager
import time
import json

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
                # problem in retrieving shop id from database
                conn.close()
                return {'error': '0', 'StatusCode': '200',
                        'shop_id': 0,
                        'Message': "No shop is defined for this user."}
        except Exception as e:
            return {'error': str(e)}


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


class GetShopProducts(Resource):
    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            # now here shop's products info must be selected from database
            '''
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
            'product_register_date': Manager.datetime_handler(row[24]),
            'product_expire_date': Manager.datetime_handler(row[25]),
            'product_like_counter': row[26],
            'product_availability': row[27],
            '''
        except Exception as e:
            return {'error': '0',
                    'Message': 'an exception happened while inserting product info into database.'
                               ' More info is: ' + str(e)}


class GetShopProfile(Resource):
    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            _user_id = content['user_id']
            _shop_id = content['shop_id']

            # check shop existence
            try:
                conn = connection.opencooncetion()
                cursor = conn.cursor()
                cursor.callproc('CheckShopExistence', (_shop_id,))
                data = cursor.fetchall()
                if len(data) > 0:
                    conn.commit()
                    conn.close()
                    # check if the current user is the owner of the shop or not
                    conn = connection.opencooncetion()
                    cursor = conn.cursor()
                    cursor.callproc('GetshopIDbyOwnerID', (_user_id,))
                    data = cursor.fetchall()
                    if len(data) > 0:
                        conn.commit()
                        conn.close()
                        if _shop_id == data[0][0]:
                            # current user is the owner
                            is_owner = True
                            # now get the shop profile
                            conn = connection.opencooncetion()
                            cursor = conn.cursor()
                            cursor.callproc('GetshopProfile', (_shop_id,))
                            data = cursor.fetchall()
                            if len(data) > 0:
                                conn.commit()
                                conn.close()
                                data_as_dict = []

                                for row in data:
                                    row_as_dict = {
                                        'is_owner': True,
                                        'shop_id': row[0],
                                        'user_table_user_id': row[1],
                                        'shop_name': row[2],
                                        'shop_picture_address': row[3],
                                        'shop_address': row[4],
                                        'shop_phone': row[5],
                                        'shop_telegram_id': row[6],
                                        'shop_category_name': row[7],
                                        'shop_description': row[8],
                                        'shop_followers_count': row[9],
                                        'shop_product_counter': row[10],
                                        'shop_city': row[11],
                                        'shop_reg_date': Manager.datetime_handler(row[12]),
                                        'is_verified': row[13],
                                    }
                                    data_as_dict.append(row_as_dict)

                                return {'error': '0',
                                        'StatusCode': '200',
                                        'shop_profile': json.dumps(data_as_dict)}
                            else:
                                conn.commit()
                                conn.close()
                                return {'error': '1', 'StatusCode': '1000',
                                        'Message': "problem in retrieving shop profile from database."}
                        else:
                            # current user is not the owner
                            # now check if this user is following the current user or not
                            conn = connection.opencooncetion()
                            cursor = conn.cursor()
                            cursor.callproc('CheckifUserisFollowingtheShop', (_user_id, _shop_id,))
                            data = cursor.fetchall()
                            if len(data) > 0:
                                # user is following the shop
                                # now get the shop profile
                                conn.commit()
                                conn.close()
                                conn = connection.opencooncetion()
                                cursor = conn.cursor()
                                cursor.callproc('GetshopProfile', (_shop_id,))
                                data = cursor.fetchall()
                                if len(data) > 0:
                                    conn.commit()
                                    conn.close()
                                    data_as_dict = []

                                    for row in data:
                                        row_as_dict = {
                                            'is_owner': False,
                                            'has_followed': True,
                                            'shop_id': row[0],
                                            'user_table_user_id': row[1],
                                            'shop_name': row[2],
                                            'shop_picture_address': row[3],
                                            'shop_address': row[4],
                                            'shop_phone': row[5],
                                            'shop_telegram_id': row[6],
                                            'shop_category_name': row[7],
                                            'shop_description': row[8],
                                            'shop_followers_count': row[9],
                                            'shop_product_counter': row[10],
                                            'shop_city': row[11],
                                            'shop_reg_date': Manager.datetime_handler(row[12]),
                                            'is_verified': row[13],
                                        }
                                        data_as_dict.append(row_as_dict)
                                    return {'error': '0',
                                            'StatusCode': '200',
                                            'shop_profile': json.dumps(data_as_dict)}
                            else:
                                # user is not following the shop
                                conn.commit()
                                conn.close()
                                conn = connection.opencooncetion()
                                cursor = conn.cursor()
                                cursor.callproc('GetshopProfile', (_shop_id,))
                                data = cursor.fetchall()
                                if len(data) > 0:
                                    conn.commit()
                                    conn.close()
                                    data_as_dict = []

                                    for row in data:
                                        row_as_dict = {
                                            'is_owner': False,
                                            'has_followed': False,
                                            'shop_id': row[0],
                                            'user_table_user_id': row[1],
                                            'shop_name': row[2],
                                            'shop_picture_address': row[3],
                                            'shop_address': row[4],
                                            'shop_phone': row[5],
                                            'shop_telegram_id': row[6],
                                            'shop_category_name': row[7],
                                            'shop_description': row[8],
                                            'shop_followers_count': row[9],
                                            'shop_product_counter': row[10],
                                            'shop_city': row[11],
                                            'shop_reg_date': Manager.datetime_handler(row[12]),
                                            'is_verified': row[13],
                                        }
                                        data_as_dict.append(row_as_dict)
                                    return {'error': '0',
                                            'StatusCode': '200',
                                            'shop_profile': json.dumps(data_as_dict)}
                else:
                    return\
                        {
                            'error': '0',
                            'StatusCode': '200',
                            'shop_id': 0,
                            'Message': "No shop is defined with this id."
                        }
            except Exception as e:
                return {'error': str(e)}
        except Exception as e:
            return {'error': str(e)}
