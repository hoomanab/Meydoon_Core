import os
import Utilities


class Manager:

    @staticmethod
    def uploadfile(file):
        # first save on disk
        path = '/currentimage'
        current_image = open(path, 'w')
        current_image.write(file)
        current_image.close()
        os.system("scp " + '/currentimage' + '31.184.132.114:/home/meydoon_image_store/currentimage')
        # ftp_connection.storbinary('STOR a.txt', file)
        # file.close()

'''
class UploadFile(Resource):

    def post(self):
        try:
            # Parse the arguments
            content = request.get_json(silent=True)

            # get the file content
            file_string = content['base64_file_string']

            # decode it from base64

            base64.b64decode(file_string)

            Utilities.FileManagement.FileManager.uploadfile(file_string)

            # save file storage path in db
            conn = connection.opencooncetion()
            cursor = conn.cursor()
            cursor.callproc('SaveImageFileStoragePath', (_user_phone_number,))
            data = cursor.fetchall()

            if len(data) > 0:
                conn.commit()
                conn.close()
                # return {'StatusCode': '200', 'Message': 'Phone number is redundant'}
            else:
                # problem in inserting user data in inactive mode
                return {'StatusCode': '1000', 'Message': str(data[0])}

        except Exception as e:
            return {'error': str(e)}
            # return {'StatusCode': '1000', 'Message': str(data[0])}

class EncodeFile(Resource):

    def post(self):
        try:
            with open("E:\working with git\git branching.png", "rb") as image_file:
                encoded_bytes = base64.b64encode(image_file.read())
                base64_string = encoded_bytes.decode('utf-8')
                python_dict_obj = {'id': 1, 'name': 'something', 'file': base64_string}
                serialized_json_str = json.dumps(python_dict_obj)
                return serialized_json_str
        except Exception as e:

            return {'error': str(e)}
            # return {'StatusCode': '1000', 'Message': str(data[0
'''