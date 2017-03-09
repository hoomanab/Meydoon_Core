# -*- coding: utf8 -*-

from flask_restful import request, Resource
import Config
import Utilities.Communication.send_sms
import Utilities.FileManagement.FileManager
import time

connection = Config.ConnectionManager.MySQLConnection()


class SaveProductInfo(Resource):
    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            _user_id = content['user_id']
            _shop_id = content['shop_id']
            _product_name = content['product_name']
            _product_category_name = content['product_category_name']
            _product_category_id = content['product_category_id']
            _product_price = content['product_price']
            _product_category_shippable_status = content['product_category_shippable_status']
            _product_verified = False
            _product_description = content['product_description']
            _product_reg_date = time.strftime('%Y-%m-%d %H:%M:%S')
            _product_like_count = 0
            _product_availability = False
            _product_image = content['product_image']

            # save into database the product info
            conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.callproc('insertNewProduct', (_shop_id, _product_name, _product_price,
                                                 _product_category_shippable_status, _product_verified,
                                                 _product_description, _product_reg_date, _product_like_count,
                                                 _product_availability))
            data = cursor.fetchone()

            if data[0] > 0:
                # product is saved in the database successfully
                # now save into database the product category info
                conn.commit()
                conn.close()

                conn = connection.opencooncetion()
                cursor = conn.cursor()
                _product_Id = data[0]
                cursor.callproc('saveProductCategory', (_product_Id, _product_category_id))
                data = cursor.fetchall()

                if len(data) == 0:
                    conn.commit()
                    conn.close()

                    # and finally save product's picture storage address on hard disk
                    storage_address = Utilities.FileManagement.FileManager.Manager.uploadfile(_product_image,
                                                                                              _product_Id, _shop_id)

                    conn = connection.opencooncetion()
                    cursor = conn.cursor()
                    cursor.callproc('updateCurrentlyInsertedProduct', (_product_Id, storage_address))
                    data = cursor.fetchall()
                    if len(data) == 0:
                        conn.commit()
                        conn.close()
                        return {'error': '0',
                                'StatusCode': '200',
                                'product_id': _product_Id,
                                'Message': 'product info completely saved into database successfully.'}
                    else:
                        conn.close()
                        # product picture storage address saving encountered an error
                        return {'error': '1',
                                'Message': 'a problem occurred. product picture storage address'
                                           ' did not inserted into database'}
                else:
                    conn.close()
                    # product category info saving encountered an error
                    return {'error': '1',
                            'Message': 'a problem occurred. product category info'
                                       ' did not inserted into database'}
            else:
                conn.close()
                # product storage encountered an error
                return {'error': '1',
                        'Message': 'a problem occurred. no product record inserted into database'}
        except Exception as e:
            return {'error': '0',
                    'Message': 'an exception happened while inserting product info into database.'
                               ' More info is: ' + str(e)}
