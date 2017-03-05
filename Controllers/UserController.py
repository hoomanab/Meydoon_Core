# -*- coding: utf8 -*-

from flask_restful import request, Resource
import Config
import time
from random import randint
import random
import Utilities.Communication.send_sms


connection = Config.ConnectionManager.MySQLConnection()


class CreateUser(Resource):

    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            _user_phone_number = content['user_phone_number']

            # check if the phone number exists already or not
            conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.callproc('checkPhoneNumberExistence', (_user_phone_number,))
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


def generateverificationcode(now, phoneNumber):

    verification_code = []
    digit_count = 6

    for i in range(digit_count):
        digit = randint(0, 9)
        verification_code.append(str(digit))

    random.shuffle(verification_code)
    strvercode = ''
    for i in range(digit_count):
        strvercode += verification_code[i]

    conn = connection.opencooncetion()
    cursor = conn.cursor()
    cursor.execute('call checkVerificationCodeExistenceandValidity(\'' + strvercode + '\', \'' + str(now) + '\', \'' +
                   str(phoneNumber) + '\');')
    data = cursor.fetchone()

    if data[0] == 0:
        conn.commit()
        conn.close()
        return int(strvercode)
    else:
        generateverificationcode(now, phoneNumber)


def generatesecondaryverificationcode(now, phoneNumber, userID):

    verification_code = []
    digit_count = 6

    for i in range(digit_count):
        digit = randint(0, 9)
        verification_code.append(str(digit))

    random.shuffle(verification_code)
    strvercode = ''
    for i in range(digit_count):
        strvercode += verification_code[i]

    conn = connection.opencooncetion()
    cursor = conn.cursor()
    cursor.execute(
        'call checkSecondaryVerificationCodeExistenceandValidity(\'' + strvercode + '\', \'' + str(now) + '\', \''
        + str(userID) + '\');')
    data = cursor.fetchone()

    if data[0] == 0:
        conn.commit()
        conn.close()
        return int(strvercode)
    else:
        generatesecondaryverificationcode(now, phoneNumber, userID)
# def executequery(self, procname , arguments ):
#
#     conn = connection.opencooncetion()
#     cursor = conn.cursor()
#     cursor.callproc(procname, args=)
#     cursor.callproc('insertNewUser', (_user_email, _user_email_verification_code, _user_email_verfied,
#                                       _user_password, _user_name, _user_regiseration_date, _user_phone_number,
#                                       _user_phone_number_verification_code, _user_phone_number_verified,
#                                       _user_telegram_id, _user_country, _user_province, _user_city,
#                                       _user_address1, _user_address2, _user_zipcode, _is_Active, _is_Banned,
#                                       _user_picture, _has_shop))
#     data = cursor.fetchall()
#
#     if len(data) is 0:
#         conn.commit()
#         conn.close()
#         return {'StatusCode': '200', 'Message': 'User creation success'}
#     else:
#         return {'StatusCode': '1000', 'Message': str(data[0])}


class AuthenticateUser(Resource):

    def post(self):
        try:
            # Parse the arguments

            # Parse the arguments
            content = request.get_json(silent=True)

            _userEmail = content['user_email']
            _userPhoneNumber = content['user_phone_number']

            conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.callproc('AuthenticateUser', (_userEmail, _userPhoneNumber))
            data = cursor.fetchall()

            if len(data) > 0:
                if str(data[0][7]) == str(_userPhoneNumber):
                    return {'status': 200, 'UserId': str(data[0][0])}
                else:
                    return {'status': 100, 'message': 'Authentication failure'}

        except Exception as e:
            return {'error': str(e)}


class GetAllUsers(Resource):

    def post(self):
        try:
            # Parse the arguments
            # Parse the arguments
            content = request.get_json(silent=True)

            conn = conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.callproc('sp_GetAllUsers')
            usersData = cursor.fetchall()

            users_list = []

            for item in usersData:
                i = {
                    'user_email': item[0],
                    'user_email_verification_code': item[1],
                    'user_email_verfied': item[2],
                    'user_password': item[3],
                    '_user_name': item[4],
                    '_user_regiseration_date': item[5],
                    '_user_phone_number': item[6],
                    '_user_phone_number_verification_code': item[7],
                    '_user_phone_number_verified': item[8],
                    '_user_telegram_id': item[9],
                    '_user_country': item[10],
                    '_user_province': item[11],
                    '_user_city': item[12],
                    '_user_address1': item[13],
                    '_user_address2': item[14],
                    '_user_zipcode': item[15],
                    '_is_Active': item[16],
                    '_is_Banned': item[17],
                    '_user_picture': item[18],
                    '_has_shop': item[19]
                }
                users_list.append(i)

            return {'StatusCode': '200', 'Items': users_list}

        except Exception as e:
            return {'error': str(e)}


class VerifyUser(Resource):
    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            _user_phone_number = content['user_phone_number']
            _user_phone_number_verification_code = content['user_phone_number_verification_code']

            is_user_verified = False
            _user_regiseration_date = None
            _user_email = None
            _user_email_verification_code = None
            _user_email_verfied = False
            _user_password = None
            _user_name = None
            conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.callproc('checkIfPhoneNumberisVerified', (_user_phone_number,))
            data = cursor.fetchall()
            if data[0][0] == 0:
                is_user_verified = False
            else:
                is_user_verified = True
            _user_telegram_id = None
            _user_country = None
            _user_province = None
            _user_city = None
            _user_address1 = None
            _user_address2 = None
            _user_zipcode = None
            _user_regiseration_date = time.strftime('%Y-%m-%d %H:%M:%S')
            conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.execute(
                'call checkVerificationCodeExistenceandValidity(\'' + _user_phone_number_verification_code + '\', \'' +
                str(_user_regiseration_date) + '\', \'' +
                str(_user_phone_number) + '\');')
            data = cursor.fetchone()

            if data[0] == 1:
                # verification code is entered correctly and is still valid
                conn.commit()
                conn.close()

                # now that the user has passed the verification successfully, activate its account
                # and save its registration date
                _is_Active = True
                _is_Banned = False
                _user_picture = None
                _has_shop = False
                _user_phone_number_verified = True

                try:
                    conn = connection.opencooncetion()
                    cursor = conn.cursor()
                    if not is_user_verified:
                        cursor.callproc('updateNewUserAfterVerification',
                                        (_user_email, _user_email_verification_code, _user_email_verfied,
                                         _user_password, _user_name, _user_regiseration_date,
                                         _user_phone_number, _user_phone_number_verification_code, _user_phone_number_verified,
                                         _user_telegram_id, _user_country, _user_province, _user_city,
                                         _user_address1, _user_address2, _user_zipcode, _is_Active, _is_Banned,
                                         _user_picture, _has_shop))

                        _user_id = cursor.fetchall()
                        conn.commit()
                        conn.close()
                        return {'error': '0',
                                'StatusCode': '200',
                                'Message': 'user verified and activated for the first time',
                                'user_id': str(_user_id[0][0]),
                                'user_phone_number': str(_user_phone_number),
                                'user_name': str(_user_name),
                                'has_shop': str(_has_shop)}
                    else:
                        # this transaction can be omitted until something else reaches to my mind!
                        cursor.callproc('updateUserAfterVerification',
                                        (_user_email, _user_email_verification_code, _user_email_verfied,
                                         _user_password, _user_name,
                                         _user_phone_number, _user_phone_number_verification_code,
                                         _user_phone_number_verified,
                                         _user_telegram_id, _user_country, _user_province, _user_city,
                                         _user_address1, _user_address2, _user_zipcode, _is_Active, _is_Banned,
                                         _user_picture, _has_shop))

                        _user_id = cursor.fetchall()
                        conn.commit()
                        conn.close()

                        # retrieve shop_id from database
                        conn = connection.opencooncetion()
                        cursor = conn.cursor()
                        cursor.callproc('GetshopIDbyOwnerID', (_user_id,))
                        data = cursor.fetchall()
                        if len(data) > 0:
                            return {'error': '0',
                                    'StatusCode': '200',
                                    'Message': 'user verified and activated once again',
                                    'user_id': str(_user_id[0][0]),
                                    'user_phone_number': str(_user_phone_number),
                                    'user_name': str(_user_name), 'shop_id': data[0][0]}
                        else:
                            # problem in retrieving user id from database
                            return {'error': '0', 'StatusCode': '200',
                                    'shop_id': None,
                                    'Message': "No shop is defined for this user."}
                except Exception as e:
                    # problem in updating currently verified and activated user
                    return {'error': '1',
                            'StatusCode': '1000',
                            'Message': 'problem in updating currently verified and activated user.'
                                       ' More info is: ' + str(e)}
            else:
                # problem in verification code; either it is entered incorrectly or it is expired
                return {'error': '1',
                        'StatusCode': '1000',
                        'Message': 'problem in verification code; either it is entered '
                                 + 'incorrectly or it is expired.'}
        except Exception as e:
            return {'error': '1',
                    'StatusCode': '1000',
                    'Message': str(e)}
