import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-key'
    #SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    #日志文件
    LOG_FILENAME = os.path.join(basedir, 'data/app.log')
    APP_PATH = '{}/app'.format(basedir)

    PER_PAGE = 20
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    #mysql数据库IP地址
    MYSQL_ADDR = '115.28.18.59'
    MYQSL_PORT = 3306
    DB_NAME = 'pdb'
    USER_NAME = 'chenke91'
    PASSWORD = 'chenke91.com'

    CACHE_TYPE ='simple'
    SQLALCHEMY_POOL_SIZE = 20
    SQLALCHEMY_POOL_TIMEOUT = 3600

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{username}:{password}@{mysql_addr}:{mysql_port}/{db_name}'.\
        format(username=USER_NAME, password=PASSWORD, mysql_addr=MYSQL_ADDR, db_name=DB_NAME, mysql_port=MYQSL_PORT)

    SITE_URL = 'http://127.0.0.1:5000'
class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir,'data-test.sqlite')

class ProductionConfig(Config):
    #mysql数据库IP地址
    MYSQL_ADDR = "127.0.0.1"
    DB_NAME = 'info'
    USER_NAME = 'info'
    PASSWORD = 'info..pwd..adsfaf324rdsf'

    CACHE_TYPE ='simple'
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PASSWORD = ''
    CACHE_REDIS_DB = 0

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{username}:{password}@{mysql_addr}/{db_name}'.\
        format(username=USER_NAME, password=PASSWORD, mysql_addr=MYSQL_ADDR, db_name=DB_NAME)

    SITE_URL = 'http://j.i3ke.com'

config = {
    'development' : DevelopmentConfig,
    'testing' : TestingConfig,
    'production' : ProductionConfig,
    'default' : DevelopmentConfig
}