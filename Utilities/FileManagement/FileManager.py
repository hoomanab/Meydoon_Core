import os
import base64
from flask_restful import Resource
import json
import io
from fabric.api import run, put, env
from fabric.contrib.files import exists
from PIL import Image
'''
import glob
import paramiko
import hashlib
'''

class Manager:

    @staticmethod
    def set_host_config(ip, user, password):
        env.host_string = ip
        env.user = user
        env.password = password

    @staticmethod
    def mkdir(folder_absolute_path):
        """
        creates new folder
        """
        run('mkdir {0}'.format(folder_absolute_path))

    @staticmethod
    def copytoremote(local_path, remote_path):

        # copy to remote server
        use_sudo = True
        put(local_path, remote_path, use_sudo)

    @staticmethod
    def uploadfile(file_content, product_Id, shop_Id):

        # first save on disk
        path = ''

        # set path based on the os on which the python app is running
        if os.name == 'posix':
            path += '/home/meydoon_image_store'

            # check if you have access
            is_accessible = os.access(path, os.F_OK)

            # if you don't create the path
            if not is_accessible:
                os.mkdir(path)

        '''elif os.name == 'nt':
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]
            for drive in drives:
                if str(drive).lower() != 'c':
                    path += str(drive).capitalize() + '\\Meydoon_image_store'
                    is_accessible = os.access(path, os.F_OK)

                    # if you don't create the path
                    if not is_accessible:
                        os.mkdir(path)
            '''
        # base on our business rules the subpath will be determined.
        if os.name == 'posix':
            path += '/products/'
            # check if you have access
            is_accessible = os.access(path, os.F_OK)

            # if you don't create the path
            if not is_accessible:
                os.mkdir(path)

            path += str(shop_Id) + '/'

            # check if you have access
            is_accessible = os.access(path, os.F_OK)

            # if you don't create the path
            if not is_accessible:
                os.mkdir(path)
        '''
        elif os.name == 'nt':
            path += '\\products\\'

            is_accessible = os.access(path, os.F_OK)

            # if you don't create the path
            if not is_accessible:
                os.mkdir(path)

            path += str(shop_Id) + '\\'

            is_accessible = os.access(path, os.F_OK)

            # if you don't create the path
            if not is_accessible:
                os.mkdir(path)
        '''
        # check now if the path exist
        os.chdir(path)

        # creating the file
        # decode base64 string and save it on disk
        imgdata = base64.b64decode(file_content)
        image = Image.open(io.BytesIO(imgdata))

        file_name = 'image' + str(product_Id)
        file_extension = '.jpg'

        # append picture file name and extension
        if os.name == 'posix':
            path += file_name + file_extension
        '''
        elif os.name == 'nt':
            path += file_name + file_extension
        '''

        image.save(path)

        # first create the necessary directory structure on the remote server
        Manager.set_host_config('31.184.132.114', 'root', 'xaas@32n53e')
        remote_path = '/home/meydoon_image_store/products/' + str(shop_Id) + '/'

        if not exists(remote_path):
            Manager.mkdir(remote_path)

        # now send the file to the storage server
        Manager.copytoremote(path, remote_path)
        # os.system("scp " + path + 'root@31.184.132.114:/home/meydoon_image_store/products/'
        #          + str(shop_Id) + '/' + file_name + file_extension)
        # RemoteFileManager.copy()

        return remote_path


class EncodeFile(Resource):

    def post(self):
        try:
            with open("E:\working with git\git branching.png", "rb") as image_file:
                file_bytes = image_file.read()
                # encoded_bytes = base64.b64encode(image_file.read())
                base64_string = base64.encodestring(file_bytes)
                _utf8_base64_encoded = base64_string.decode('utf-8')
                # python_dict_obj = {'id': 1, 'name': 'something', 'file': encoded_string}
                # serialized_json_str = json.dumps(python_dict_obj)
                serialized_json_str = json.dumps({'file': _utf8_base64_encoded})
                return serialized_json_str
                # return {'file': encoded_string}
        except Exception as e:

            return {'error': str(e)}
            # return {'StatusCode': '1000', 'Message': str(data[0

#!/usr/bin/env python

## Copy files unattended over SSH using a glob pattern.
## It tries first to connect using a private key from a private key file
## or provided by an SSH agent. If RSA authentication fails, then
## password login is attempted.

##
## DEPENDENT MODULES:
##      * paramiko, install it with `easy_install paramiko`

## NOTE: 1. The script assumes that the files on the source
##       computer are *always* newer that on the target;
##       2. no timestamps or file size comparisons are made
##       3. use at your own risk

'''
hostname = '131.184.132.114' # remote hostname where SSH server is running
port = 22
username = 'root'
password = 'xaas@32n53e'
rsa_private_key = r"/home/paramikouser/.ssh/rsa_private_key"

dir_local='/home/paramikouser/local_data'
dir_remote = "remote_machine_folder/subfolder"
glob_pattern='*.*'

class RemoteFileManager:
    @staticmethod
    def agent_auth(transport, username):
        """
        Attempt to authenticate to the given transport using any of the private
        keys available from an SSH agent or from a local private RSA key file (assumes no pass phrase).
        """
        try:
            ki = paramiko.RSAKey.from_private_key_file(rsa_private_key)
        except Exception as e:
            print('Failed loading' % (rsa_private_key, e))

        agent = paramiko.Agent()
        agent_keys = agent.get_keys() + (ki,)
        if len(agent_keys) == 0:
            return

        for key in agent_keys:
            print('Trying ssh-agent key %s' % key.get_fingerprint().encode('hex'),)
            try:
                transport.auth_publickey(username, key)
                print('... success!')
                return
            except paramiko.SSHException as e:
                print('... failed!', e)
    @staticmethod
    def copy():
        # get host key, if we know one
        hostkeytype = None
        hostkey = None
        files_copied = 0
        try:
            host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        except IOError:
            try:
                # try ~/ssh/ too, e.g. on windows
                host_keys = paramiko.util.load_host_keys(os.path.expanduser('~/ssh/known_hosts'))
            except IOError:
                print('*** Unable to open host keys file')
                host_keys = {}

        if host_keys.has_key(hostname):
            hostkeytype = host_keys[hostname].keys()[0]
            hostkey = host_keys[hostname][hostkeytype]
            print('Using host key of type %s' % hostkeytype)

        # now, connect and use paramiko Transport to negotiate SSH2 across the connection
        try:
            print('Establishing SSH connection to:', hostname, port, '...')
            t = paramiko.Transport((hostname, port))
            t.start_client()

            RemoteFileManager.agent_auth(t, username)

            if not t.is_authenticated():
                print('RSA key auth failed! Trying password login...')
                t.connect(username=username, password=password, hostkey=hostkey)
            else:
                sftp = t.open_session()
            sftp = paramiko.SFTPClient.from_transport(t)

            # dirlist on remote host
        #    dirlist = sftp.listdir('.')
        #    print "Dirlist:", dirlist

            try:
                sftp.mkdir(dir_remote)
            except IOError as e:
                print('(assuming ', dir_remote, 'exists)', e)

        #    print 'created ' + dir_remote +' on the hostname'

            # BETTER: use the get() and put() methods
            # for fname in os.listdir(dir_local):

            for fname in glob.glob(dir_local + os.sep + glob_pattern):
                is_up_to_date = False
                if fname.lower().endswith('xml'):
                    local_file = os.path.join(dir_local, fname)
                    remote_file = dir_remote + '/' + os.path.basename(fname)

                    #if remote file exists
                    try:
                        if sftp.stat(remote_file):
                            local_file_data = open(local_file, "rb").read()
                            remote_file_data = sftp.open(remote_file).read()
                            md1 = hashlib.md5.new(local_file_data).digest()
                            md2 = hashlib.md5.new(remote_file_data).digest()
                            if md1 == md2:
                                is_up_to_date = True
                                print("UNCHANGED:", os.path.basename(fname))
                            else:
                                print("MODIFIED:", os.path.basename(fname),)
                    except:
                        print("NEW: ", os.path.basename(fname),)

                    if not is_up_to_date:
                        print('Copying', local_file, 'to ', remote_file)
                        sftp.put(local_file, remote_file)
                        files_copied += 1
            t.close()

        except Exception as e:
            print('*** Caught exception: %s: %s' % (e.__class__, e))
            try:
                t.close()
            except:
                pass
        print('=' * 60)
        print('Total files copied:',files_copied)
        print('All operations complete!')
        print('=' * 60)
'''