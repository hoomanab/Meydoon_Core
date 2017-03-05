# -*- coding: utf8 -*-

from flask_restful import request, Resource
import Config
import time
import Utilities.Communication.send_sms
import Utilities.FileManagement.FileManager


connection = Config.ConnectionManager.MySQLConnection()

class SaveProductInfo(Resource):

    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            _user_id = content['user_id']
            _product_name = content['product_name']
            # _product_category_name = content['product_category_name']
            # _product_category_id = content['product_category_id']
            # _product_category_shippable_status = content['_product_category_shippable_status']
            # _product_description = content['product_description']
            _product_image = content['product_image']
            Utilities.FileManagement.FileManager.Manager.uploadfile(_product_image)

            # save into databse the product info
            conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.callproc('checkPhoneNumberExistence', (_user_id,))
            data = cursor.fetchall()
            if len(data) == 0:
                # phone number entered is new
                # so insert a new user in the database
                _user_email = None
                _user_email_verification_code = 0
                _user_email_verfied = False
                _user_password = ""
                _user_name = ""
                _user_initial_reg_date = time.strftime('%Y-%m-%d %H:%M:%S')
                _user_regiseration_date = None
                _user_phone_number_verification_code = 0
                _user_phone_number_verified = False
                _user_telegram_id = None
                _user_country = ""
                _user_province = ""
                _user_city = ""
                _user_address1 = ""
                _user_address2 = ""
                _user_zipcode = 0
                _is_Active = False
                _is_Banned = False
                _user_picture = None
                _has_shop = False

                conn = connection.opencooncetion()
                cursor = conn.cursor()
                cursor.callproc('insertNewUser', (_user_email, _user_email_verification_code, _user_email_verfied,
                                                  _user_password, _user_name, _user_regiseration_date,
                                                  _user_phone_number,
                                                  _user_phone_number_verification_code, _user_phone_number_verified,
                                                  _user_telegram_id, _user_country, _user_province, _user_city,
                                                  _user_address1, _user_address2, _user_zipcode, _is_Active, _is_Banned,
                                                  _user_picture, _has_shop, _user_initial_reg_date))
                data = cursor.fetchall()

                if len(data) is 0:
                    conn.commit()
                    conn.close()
                    # new user record saved in inactive mode
                    _user_phone_number_verification_code = generateverificationcode(_user_initial_reg_date,
                                                                                    _user_phone_number)
                    # save verification code
                    conn = connection.opencooncetion()
                    cursor = conn.cursor()
                    cursor.callproc('saveVerificationCode', (_user_phone_number_verification_code, _user_phone_number))
                    data = cursor.fetchall()
                    if len(data) is 0:
                        conn.commit()
                        conn.close()
                        # verification code saved in db so sending it via sms
                        Utilities.Communication.send_sms.SMS.send(_user_phone_number,
                                                                  _user_phone_number_verification_code)
                        return {'error': '0', 'StatusCode': '200',
                                'Message': 'user saved in inactive mode without'
                                + 'profile data and verification code generated and sms-ed to.'}
                    else:
                        # problem in saving phone number verification code
                        return {'error': '1', 'StatusCode': '1000',
                                'Message': 'problem in saving phone number verification code'
                                           + ' more info is: ' + str(data[0])}
                else:
                    # problem in inserting user data in inactive mode into database
                    return {'error': '1', 'StatusCode': '1000',
                            'Message': 'problem in inserting user data in inactive mode into database' +
                                       ' more info is: ' + str(data[0])}

            elif len(data) > 0:
                conn.commit()
                conn.close()
                # Phone number is redundant
                # user is trying to login with another (mobile) device after it has completed
                # initial signup and verification or user is returning back after entering its
                # phone number but before completing the verification process
                # check if user isVerified or not (in both cases the same procedure is going to
                # be performed but if/else is used for future discriminations
                conn = connection.opencooncetion()
                cursor = conn.cursor()
                cursor.callproc('checkIfPhoneNumberisVerified', (_user_phone_number,))
                data = cursor.fetchall()
                if data[0][0] == 1:
                    # user phone number is verified so it is using another device or
                    # has logged out and is again coming back to use the app
                    conn.commit()
                    conn.close()
                    # get userID
                    conn = connection.opencooncetion()
                    cursor = conn.cursor()
                    cursor.callproc('getUserIDbyPhoneNumber', (_user_phone_number,))
                    data = cursor.fetchall()
                    if len(data) > 0:
                        conn.commit()
                        conn.close()
                        _user_id = data[0][0]
                        # user_id obtained. now generate a new verification code for it
                        _user_phone_number_verification_code = generatesecondaryverificationcode(
                            time.strftime('%Y-%m-%d %H:%M:%S'), _user_phone_number, _user_id)

                        # save verification code
                        conn = connection.opencooncetion()
                        cursor = conn.cursor()
                        cursor.callproc('saveVerificationCode',
                                        (_user_phone_number_verification_code, _user_phone_number))

                        data = cursor.fetchall()

                        if len(data) is 0:
                            conn.commit()
                            conn.close()
                            # verification code saved in db so sending it via sms
                            Utilities.Communication.send_sms.SMS.send(_user_phone_number,
                                                                      _user_phone_number_verification_code)
                            return {'error': '0', 'StatusCode': '200',
                                    'Message': 'new verification code generated and saved '
                                               'for the already verified user and sms-ed to.'}
                        else:
                            # problem in saving phone number new verification code
                            return {'error': '1', 'StatusCode': '1000',
                                    'Message': 'problem in saving phone number new verification code'
                                               + ' more info is: ' + str(data[0])}
                    else:
                        # problem in retrieving user id from database
                        return {'error': '1', 'StatusCode': '1000',
                                'Message': 'problem in retrieving user id from database'
                                           + ' more info is: ' + str(data[0])}
                else:
                    # phone number is not verified so its a returning user after initial abortive attempt
                    conn.commit()
                    conn.close()
                    # get userID
                    conn = connection.opencooncetion()
                    cursor = conn.cursor()
                    cursor.callproc('getUserIDbyPhoneNumber', (_user_phone_number,))
                    data = cursor.fetchall()
                    if len(data) > 0:
                        conn.commit()
                        conn.close()
                        _user_id = data[0][0]

                        # user_id obtained. now generate a new verification code for it
                        _user_phone_number_verification_code = generatesecondaryverificationcode(
                            time.strftime('%Y-%m-%d %H:%M:%S'), _user_phone_number, _user_id)

                        # save verification code
                        conn = connection.opencooncetion()
                        cursor = conn.cursor()
                        cursor.callproc('saveVerificationCode',
                                        (_user_phone_number_verification_code, _user_phone_number))

                        data = cursor.fetchall()

                        if len(data) is 0:
                            conn.commit()
                            conn.close()
                            # verification code saved in db so sending it via sms
                            Utilities.Communication.send_sms.SMS.send(_user_phone_number,
                                                                      _user_phone_number_verification_code)
                            return {'error': '0', 'StatusCode': '200',
                                    'Message': 'new verification code generated and saved '
                                               'for the not already verified returning user and sms-ed to.'}
                        else:
                            # problem in saving phone number new verification code
                            return {'error': '1', 'StatusCode': '1000',
                                    'Message': 'problem in saving phone number new verification code'
                                               + ' more info is: ' + str(data[0])}
                    else:
                        # problem in retrieving user id from database
                        return {'error': '1', 'StatusCode': '1000',
                                'Message': 'problem in retrieving user id from database'
                                           + ' more info is: ' + str(data[0])}
        except Exception as e:

            return {'error': str(e)}
            # return {'StatusCode': '1000', 'Message': str(data[0])}

