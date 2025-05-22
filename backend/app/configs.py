# backend/app/configs.py
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os

# 构建.env文件的绝对路径(假设.env在backend目录下,configs.py在backend/app/下)
# Path(__file__) 获取当前文件(configs.py)的路径
# .parent 获取configs.py的父目录 (app/)
# .parent.parent 获取app/的父目录 (backend/)
# 然后与 '.env' 文件名拼接
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """基础配置类，包含所有环境通用的配置"""
    SECRET_KEY = os.getenv("SECRET_KEY", "a_very_default_and_insecure_secret_key")  # Flask应用本身的密钥

    # SQLAlchemy 配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭Flask-SQLAlchemy的事件通知系统，以减少开销
    SQLALCHEMY_ECHO = False  # 默认情况下，不打印SQLAlchemy执行的SQL语句

    # JWT (JSON Web Token) 配置
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "another_default_and_insecure_jwt_secret_key")  # 用于签名JWT的密钥
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "30")))  # Access Token有效期
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_DAYS", "14")))  # Refresh Token有效期
    JWT_BLACKLIST_ENABLED = True  # 启用Token黑名单功能 (用于Token吊销)
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]  # 指定哪些类型的Token需要检查黑名单


class DevelopmentConfig(Config):
    """开发环境特定配置"""
    DEBUG = True  # 开启Flask的调试模式
    SQLALCHEMY_ECHO = True  # 开发时打印所有执行的SQL语句，便于调试

    # 开发数据库连接信息 (从.env文件读取，如果未设置则使用默认值)
    DB_USER = os.getenv("DEV_DB_USER", "root")
    DB_PASSWORD = os.getenv("DEV_DB_PASSWORD", "your_dev_db_password")  # 强烈建议在.env中设置真实密码
    DB_HOST = os.getenv("DEV_DB_HOST", "localhost")
    DB_PORT = os.getenv("DEV_DB_PORT", "3306")
    DB_NAME = os.getenv("DEV_DB_NAME", "flask_vue_dev_db")  # 开发数据库名
    SQLALCHEMY_DATABASE_URI = \
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'


class TestingConfig(Config):
    """测试环境特定配置"""
    TESTING = True  # 开启Flask的测试模式
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI', 'sqlite:///:memory:')  # 测试通常使用内存中的SQLite数据库
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)  # 测试时Token有效期设置得很短，方便测试过期逻辑
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=10)
    # 在测试配置中，通常会禁用CSRF保护（如果使用了Flask-WTF等）


class ProductionConfig(Config):
    """生产环境特定配置"""
    DEBUG = False  # 生产环境必须关闭调试模式
    SQLALCHEMY_ECHO = False  # 生产环境不打印SQL语句

    # 生产数据库凭证必须通过环境变量配置，不应有默认值或硬编码
    DB_USER = os.getenv("PROD_DB_USER")
    DB_PASSWORD = os.getenv("PROD_DB_PASSWORD")
    DB_HOST = os.getenv("PROD_DB_HOST")
    DB_PORT = os.getenv("PROD_DB_PORT")
    DB_NAME = os.getenv("PROD_DB_NAME")

    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        # 在应用启动时检查生产数据库配置的完整性
        raise ValueError("生产环境数据库配置不完整! "
                         "请设置PROD_DB_USER, PROD_DB_PASSWORD, PROD_DB_HOST, PROD_DB_PORT, PROD_DB_NAME环境变量。")

    SQLALCHEMY_DATABASE_URI = \
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'


# 配置名称到配置类的映射字典，方便应用工厂根据名称选择配置
config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig,
    default=DevelopmentConfig  # 如果未指定FLASK_CONFIG，则使用默认配置
)


def get_current_config() -> Config:
    """获取当前配置实例"""
    config_name = os.getenv('FLASK_CONFIG', 'default')
    return config_by_name[config_name]()
