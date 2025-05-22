# backend/app/__init__.py
from flask import Flask, jsonify
from loguru import logger
import os  # 添加os导入，因为下面会用到

# 从同级目录的configs.py导入配置映射和获取当前配置实例的函数
from .configs import config_by_name, get_current_config
# 从同级目录的extensions.py导入我们创建的扩展实例
from .extensions import db, jwt, cors, configure_logging


# 由于不使用Flask-Migrate，从extensions.py移除了migrate的导入

def create_app(config_object=None) -> Flask:
    """
    应用工厂函数：创建并配置Flask应用实例。
    :param config_object: (可选) 配置名称字符串或直接传入配置对象。如果为None，则会尝试从环境变量FLASK_CONFIG加载。
    :return: 配置好的Flask应用实例。
    """
    app = Flask(__name__, instance_relative_config=True)  # instance_relative_config=True允许从instance/文件夹加载配置

    # 1. 加载应用配置
    active_config_name = "default"
    
    if config_object is None:
        # 没有提供配置，使用get_current_config()获取默认配置
        current_config_obj = get_current_config()
        app.config.from_object(current_config_obj)
        active_config_name = os.getenv('FLASK_CONFIG', 'default')
    elif isinstance(config_object, str):
        # 如果提供的是字符串配置名，从config_by_name字典获取对应的配置类
        if config_object in config_by_name:
            app.config.from_object(config_by_name[config_object])
            active_config_name = config_object
        else:
            # 找不到指定的配置名，使用默认配置
            app.config.from_object(config_by_name['default'])
            active_config_name = 'default'
            logger.warning(f"配置名 '{config_object}' 无效，使用默认配置")
    else:
        # 直接传入了配置对象
        app.config.from_object(config_object)
        active_config_name = "custom_object"

    # 2. 配置并初始化日志
    configure_logging(app.config)  # 将配置对象传给日志配置函数
    logger.info(f"应用 '{app.name}' 正在以 '{active_config_name}' 配置启动...")
    logger.debug(f"数据库URI: {app.config.get('SQLALCHEMY_DATABASE_URI', '未设置')}")
    logger.debug(f"JWT密钥已设置: {'是的' if app.config.get('JWT_SECRET_KEY') else '否，请检查.env文件！'}")

    # 3. 初始化Flask扩展
    db.init_app(app)  # 初始化SQLAlchemy
    # migrate.init_app(app, db) # 由于不使用Flask-Migrate，此行移除或注释掉
    jwt.init_app(app)  # 初始化Flask-JWT-Extended
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})  # 初始化CORS

    # 4. 导入数据模型
    # 这一步确保SQLAlchemy在运行时能"感知"到这些模型。
    # 我们将模型定义在 app/models/ 目录下。
    # 使用app.app_context()确保在导入模型时应用上下文是激活的，
    # 这对于某些依赖app.config的模型定义或SQLAlchemy操作是必要的。
    with app.app_context():
        from .models import user_model, token_model  # 从app.models包 (models/__init__.py) 导入
        # 确保 User 和 TokenBlocklist 在 models/__init__.py 中被导入或定义

    # 5. 注册JWT相关的回调函数 (例如Token黑名单检查)
    @jwt.token_in_blocklist_loader
    def check_if_jti_in_blocklist(jwt_header: dict, jwt_payload: dict) -> bool:
        """
        此回调函数由Flask-JWT-Extended在验证Token时调用，
        用于检查Token的JTI是否已存在于数据库的TokenBlocklist表中。
        """
        jti = jwt_payload["jti"]
        # 使用正确的模型引用 (token_model.TokenBlocklist)
        # .one_or_none() 是一个安全的查询方式，如果记录不存在返回None，存在多个则报错
        token_entry = token_model.TokenBlocklist.query.filter_by(jti=jti).one_or_none()
        is_revoked = token_entry is not None
        if is_revoked:
            logger.debug(f"Token JTI '{jti}' 存在于数据库黑名单中 (已吊销).")
        return is_revoked

    # 6. 注册API蓝图 (将在后续章节定义蓝图文件后取消注释)
    from .apis.auth_api import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')



    from .apis.user_api import user_bp
    app.register_blueprint(user_bp, url_prefix='/api')  # user_api中的/me路由将是 /api/me



    logger.info(f"应用 '{app.name}' 已成功配置并初始化。蓝图和JWT回调已设置。")
    return app