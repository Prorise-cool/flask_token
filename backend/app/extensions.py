# backend/app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from loguru import logger

# 1. 创建扩展实例，但不进行初始化 (不传入app参数)
# 这些实例将在应用工厂函数中通过调用各自的 .init_app(app) 方法进行初始化。
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()  # 初始化CORS实例，后续在工厂中用init_app进一步配置


# 2. (可选) 定义一个通用的日志配置函数
def configure_logging(current_app_config):
    """
    根据应用配置来设置Loguru日志。
    :param current_app_config: 当前加载的Flask配置对象 (例如 DevelopmentConfig实例)
    """
    # 安全地获取DEBUG标志，如果不存在则默认为False
    is_debug = current_app_config.get('DEBUG', False)
    log_level = "DEBUG" if is_debug else "INFO"
    
    # 移除旧的日志处理器，以防重复添加 (尤其是在热重载时)
    logger.remove()

    # 为开发环境添加彩色控制台输出
    if is_debug or current_app_config.get('TESTING', False):
        logger.add(
            lambda _: None,  # 空sink，因为我们只想格式化输出到stderr
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level,
            colorize=True,
            enqueue=True  # 异步写入，提高性能
        )
    else:
        # 生产环境的日志配置 (可以配置输出到文件、syslog、ELK等)
        # logger.add(
        #     "logs/production.log",
        #     rotation="10 MB", # 每个日志文件最大10MB
        #     retention="1 week", # 日志保留1周
        #     compression="zip", # 压缩旧日志
        #     level="INFO",
        #     format="{time} {level} {message}",
        #     enqueue=True
        # )
        # 为简洁，生产环境也暂时输出到控制台，但格式不同
        logger.add(
            lambda _: None,
            format="{time} {level} {message}",
            level="INFO",
            enqueue=True
        )
    logger.info(f"Loguru日志已配置，级别: {log_level}")
