import Config


class MySQLConnection:

    @staticmethod
    def  setupconnection():

        # MySQL configurations
        Config.app.config['MYSQL_DATABASE_USER'] = 'root'
        Config.app.config['MYSQL_DATABASE_PASSWORD'] = '@root123'
        Config.app.config['MYSQL_DATABASE_DB'] = 'Meydoon'
        Config.app.config['MYSQL_DATABASE_HOST'] = '31.184.130.108'

        Config.mysql.init_app(Config.app)

    def opencooncetion(self):
        return Config.mysql.connect()

    def terminatecooncetion(self):
        Config.mysql.teardown_request()
