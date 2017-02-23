import Config
import Controllers.UserController

connection = Config.ConnectionManager.MySQLConnection()


@Config.app.route('/')
def index():
    return 'Hello World!'

Config.api.add_resource(Controllers.UserController.CreateUser, '/CreateUser')
Config.api.add_resource(Controllers.UserController.AuthenticateUser, '/AuthenticateUser')
Config.api.add_resource(Controllers.UserController.GetAllUsers, '/GetAllItems')

if __name__ == '__main__':
    Config.app.run(debug=True)
