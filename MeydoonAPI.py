import os

import Config
import Controllers.UserController

connection = Config.ConnectionManager.MySQLConnection()


@Config.app.route('/')
def index():
    return 'Hello World!'

Config.api.add_resource(Controllers.UserController.CreateUser, '/CreateUser')
Config.api.add_resource(Controllers.UserController.AuthenticateUser, '/AuthenticateUser')
Config.api.add_resource(Controllers.UserController.GetAllUsers, '/GetAllItems')
Config.api.add_resource(Controllers.UserController.VerifyUser, '/VerifyUser')


if __name__ == '__main__':
    # Config.app.run(debug=True)
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    Config.app.run(host='0.0.0.0', port=port)
