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
            # _user_email = content['user_email']
            # _user_email_verification_code = content['user_email_verification_code']
            # _user_email_verfied = content['user_email_verfied']
            # _user_password = content['user_password']
            # _user_name = content['user_name']
            # _user_regiseration_date = content['user_regiseration_date']
            # _user_phone_number_verification_code = content['user_phone_number_verification_code']
            # _user_phone_number_verified = content['user_phone_number_verified']
            # _user_telegram_id = content['user_telegram_id']
            # _user_country = content['user_country']
            # _user_province = content['user_province']
            # _user_city = content['user_city']
            # _user_address1 = content['user_address1']
            # _user_address2 = content['user_address2']
            # _user_zipcode = content['user_zipcode']
            # _is_Active = content['is_Active']
            # _is_Banned = content['is_Banned']
            # _user_picture = content['user_picture']
            # _has_shop = content['has_shop']

            _user_email = None
            _user_email_verification_code = 0
            _user_email_verfied = False
            _user_password = ""
            _user_name = ""
            _user_regiseration_date = time.strftime("%c")
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
            _user_initial_reg_date = time.strftime("%c")

            #check if the phone number exists already or not
            conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.callproc('checkPhoneNumberExistence', (_user_phone_number,))
            data = cursor.fetchall()

            if len(data) > 0:
                conn.commit()
                conn.close()
                return {'StatusCode': '200', 'Message': 'Phone number is redundant'}
            else:
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
                    _user_phone_number_verification_code = generateverificationcode()
                    # save verification code
                    conn = connection.opencooncetion()
                    cursor = conn.cursor()
                    cursor.callproc('saveVerificationCode', (_user_phone_number_verification_code, _user_phone_number))
                    data = cursor.fetchall()
                    if len(data) is 0:
                        conn.commit()
                        conn.close()
                        # send it via sms
                        Utilities.Communication.send_sms.SMS.send()
                        return {'StatusCode': '200', 'Message': "user save in inactive mode with profile info and "
                                                                "verification code created and smsed to."}
                    else:
                        # problem in saving phone number verification code
                        return {'StatusCode': '1000', 'Message': str(data[0])}
                else:
                    # problem in inserting user data in inactive mode
                    return {'StatusCode': '1000', 'Message': str(data[0])}

        except Exception as e:

            return {'error': str(e)}
            # return {'StatusCode': '1000', 'Message': str(data[0])}


def generateverificationcode():

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
    cursor.callproc('checkVerificationCodeExistenceandValidity', (int(strvercode), time.strftime("%c")))
    data = cursor.fetchall()

    if len(data) is 0:
        conn.commit()
        conn.close()
        return int(strvercode)
    else:
        generateverificationcode()

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
            # _user_email = content['user_email']
            # _user_email_verification_code = content['user_email_verification_code']
            # _user_email_verfied = content['user_email_verfied']
            # _user_password = content['user_password']
            # _user_name = content['user_name']
            # _user_regiseration_date = content['user_regiseration_date']
            # _user_phone_number_verification_code = content['user_phone_number_verification_code']
            # _user_phone_number_verified = content['user_phone_number_verified']
            # _user_telegram_id = content['user_telegram_id']
            # _user_country = content['user_country']
            # _user_province = content['user_province']
            # _user_city = content['user_city']
            # _user_address1 = content['user_address1']
            # _user_address2 = content['user_address2']
            # _user_zipcode = content['user_zipcode']
            # _is_Active = content['is_Active']
            # _is_Banned = content['is_Banned']
            # _user_picture = content['user_picture']
            # _has_shop = content['has_shop']

            _user_email = None
            _user_email_verification_code = 0
            _user_email_verfied = False
            _user_password = ""
            _user_name = ""
            _user_regiseration_date = time.strftime("%c")
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
            _user_initial_reg_date = time.strftime("%c")

            conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.callproc('checkVerificationCodeExistenceandValidity', (int(_user_phone_number_verification_code), time.strftime("%c")))
            data = cursor.fetchall()

            if len(data) > 0:
                # verification code is entered correctly and is still valid
                conn.commit()
                conn.close()

                # now that the user has passed the verification activate its account and save its registration date
                _user_regiseration_date = time.strftime("%c")
                _is_Active = True
                _is_Banned = False
                _user_picture = None
                _has_shop = False

                conn = connection.opencooncetion()
                cursor = conn.cursor()
                cursor.callproc('updateNewUserAfterVerification',
                                (_user_email, _user_email_verification_code, _user_email_verfied,
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
                    return {'StatusCode': '200', 'Message': 'user verified and activated'}
                else:
                    # problem in updating currently verified and activated user
                    return {'StatusCode': '1000', 'Message': str(data[0])}

            else:
                # problem in verification code; either it is entered incorrectly or it is expired
                return {'StatusCode': '1000', 'Message': 'problem in verification code; either it is entered '
                                                         + 'incorrectly or it is expired'}

        except Exception as e:

            return {'error': str(e)}
            # return {'StatusCode': '1000', 'Message': str(data[0])}
