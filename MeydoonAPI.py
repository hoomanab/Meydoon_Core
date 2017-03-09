import os

import Config
import Controllers.UserController
import Controllers.ProductController
import Controllers.ShopController
import Utilities.FileManagement.FileManager
import Controllers.HomeFeedController

connection = Config.ConnectionManager.MySQLConnection()


@Config.app.route('/')
def index():
    return 'Hello World!'

Config.api.add_resource(Controllers.UserController.CreateUser, '/CreateUser')
Config.api.add_resource(Controllers.UserController.AuthenticateUser, '/AuthenticateUser')
Config.api.add_resource(Controllers.UserController.GetAllUsers, '/GetAllUsers')
Config.api.add_resource(Controllers.UserController.VerifyUser, '/VerifyUser')
Config.api.add_resource(Utilities.FileManagement.FileManager.EncodeFile, '/EncodeFile')
Config.api.add_resource(Controllers.ProductController.SaveProductInfo, '/SaveProduct')
Config.api.add_resource(Controllers.ShopController.SaveShopInfo, '/SaveShop')
Config.api.add_resource(Controllers.HomeFeedController.GetGuestUserHomeFeed, '/GetGuestFeed')
Config.api.add_resource(Controllers.ShopController.GetshopIDbyOwnerID, '/GetShopId')
Config.api.add_resource(Controllers.HomeFeedController.GetAuthenticatedUserHomeFeed, '/GetAuthenticatedFeed')

if __name__ == '__main__':
    # Config.app.run(debug=True)
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    Config.app.run(host='0.0.0.0', port=port)
