# backend/run.py
import os
from app import create_app  # 从 app 包 (app/__init__.py) 导入 create_app 工厂函数

# 从环境变量 FLASK_CONFIG 获取配置名称，如果未设置，则 create_app 会使用默认配置('dev')
# create_app 函数内部会处理 config_name 为 None 的情况
config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

if __name__ == '__main__':
    # `flask run` 命令会使用 FLASK_DEBUG, FLASK_RUN_HOST, FLASK_RUN_PORT 环境变量。
    # 如果直接通过 `python run.py` 运行，这些需要在 app.run() 中明确指定或从配置读取。
    # app.config['DEBUG'] 会根据 FLASK_CONFIG (例如 'dev') 从 DevelopmentConfig 设置。
    run_host = os.getenv('FLASK_RUN_HOST', '127.0.0.1')
    run_port = int(os.getenv('FLASK_RUN_PORT', '5000'))

    # 获取当前配置的DEBUG状态来决定是否以debug模式运行
    # 注意：FLASK_DEBUG=1 环境变量会覆盖 app.config['DEBUG'] 当使用 `flask run` 时。
    # 但直接运行 python run.py 时，app.config['DEBUG'] 更可靠。
    is_debug_enabled = app.config.get('DEBUG', False)

    app.run(host=run_host, port=run_port, debug=is_debug_enabled)