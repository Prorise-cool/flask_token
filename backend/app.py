# backend/app.py
from datetime import timedelta
import os

from flask import Flask, request, jsonify  # 确保 request 已导入
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, \
    get_jwt
from pyexpat.errors import messages
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
# 引入我们基础篇章用到的日志库
from loguru import logger  # 导入 Loguru

# from datetime import timedelta # 如果需要配置 token 有效期

load_dotenv()
app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default-super-secret-key-for-dev")  # 设置 JWT 密钥
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=10)  # 设置访问令牌的有效期为 三十秒
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)  # 设置刷新令牌的有效期为 7 天
app.config["JWT_BLACKLIST_ENABLED"] = True  # 为后续登出吊销 Token 做准备
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]  # 检查吊销的 Token 类型

CORS(app, resources={r"/api/*": {" origins ": "*"}})  # 允许所有来源访问/api/*路径
jwt = JWTManager(app)


# 这个回调函数用于检查JWT令牌是否在黑名单中
# 当用户登出或管理员吊销令牌时，我们会将令牌的唯一标识符(jti)添加到黑名单中
# Flask-JWT-Extended会在每次请求时调用此回调，检查令牌是否被吊销
# 如果返回True，表示令牌在黑名单中，请求将被拒绝并返回401错误
# 这是实现安全登出和令牌吊销功能的关键机制
@jwt.token_in_blocklist_loader
def check_if_jti_in_blocklist(jwt_header: dict, jwt_payload: dict) -> bool:
    """
    回调函数，检查给定的JWT的jti是否已被加入黑名单。
    Flask-JWT-Extended会在验证每个受保护请求的Token时调用此函数。
    """
    jti = jwt_payload["jti"] # 'jti'是JWT的唯一标识符声明
    is_revoked = jti in TOKEN_BLOCKLIST
    if is_revoked:
        logger.info(f"Token JTI '{jti}' 在黑名单中。")
    return is_revoked

# 简易内存用户存储和 Token 黑名单
users_in_memory_store: dict[str, dict] = {}
TOKEN_BLOCKLIST: set[str] = set()  # 为后续登出吊销 Token 做准备


# --- Token 知识点：密码哈希 ---
# 永远不要存储明文密码！密码必须经过哈希处理。
# 哈希是将任意长度的输入通过哈希算法转换成固定长度的输出（哈希值）。
# 好的哈希算法具有以下特点：
# 1. 单向性：从哈希值很难（计算上不可行）反推出原始输入。
# 2. 抗碰撞性：很难找到两个不同的输入产生相同的哈希值。
# 3. 雪崩效应：原始输入的微小改变会导致哈希值巨大变化。
# `werkzeug.security.generate_password_hash` 会自动使用安全的哈希算法（如 scrypt 或 pbkdf2_sha256）并加入“盐”（salt），
# “盐”是一个随机数据，与密码结合后再进行哈希，使得相同的密码也会产生不同的哈希值，能有效抵抗彩虹表攻击。
@app.route('/api/auth/register', methods=['POST'])
def register_user_api() -> tuple[jsonify, int]:
    data = request.get_json()
    if not data:
        return jsonify({"messages": "请求体不能为空且必须为Json格式"}), 400

    username: str = data.get("username")
    password: str = data.get("password")

    if not username or not password:
        return jsonify({"messages": "用户名和密码不能为空"}), 400
    if len(password) < 6:
        return jsonify({"messages": "密码不能少于六位数！"}), 400

    if not username.strip():  # 去除字符串开头和结尾的空白字符
        return jsonify({"messages": "用户名不能全为空白字符！"}), 400

    if username in users_in_memory_store:
        return jsonify({"messages": f"用户名 {username}已存在"}), 400

    hashed_password = generate_password_hash(password)
    users_in_memory_store[username] = {"hashed_password": hashed_password}
    logger.info(f"用户 '{username}' 注册成功。当前用户池: {users_in_memory_store}")
    return jsonify({"message": "注册成功", "status": 200}), 201


@app.route("/api/auth/login", methods=["POST"])
def login_user_pai() -> tuple[jsonify, int]:
    data = request.get_json()
    if not data:
        return jsonify({"messages": "请求体不能为空且必须为Json格式"}), 400

    username: str = data.get("username")
    password: str = data.get("password")

    if not username or not password:
        return jsonify({"messages": "用户名和密码不能为空"}), 400

    user_data = users_in_memory_store.get(username)

    # --- Token 知识点：密码验证 ---
    # 使用 `check_password_hash` 来比较用户输入的密码（会自动哈希）与存储的哈希值。
    # 不能直接比较明文密码或自己哈希后再比较，因为盐值不同会导致相同明文密码的哈希值也不同
    if user_data and check_password_hash(user_data["hashed_password"], password):
        # --- Token 知识点：Token的两个核心函数与参数 ---
        # 1. `identity`: 唯一标识用户。可以是用户 ID、用户名等。它将成为 JWT Payload 中 `sub` (Subject)声明的值。
        # 2. `fresh=True`: 表示这个 Access Token 是通过用户直接输入凭证获得的，是“新鲜的”。
        #    某些敏感操作可能要求 Token 必须是新鲜的。
        # 3. `create_access_token`: 生成寿命较短的 Access Token，用于访问受保护资源。
        # 4. `create_refresh_token`: 生成寿命较长的 Refresh Token，用于在 Access Token 过期后获取新的 Access Token。
        access_token: str = create_access_token(identity=username, fresh=True)
        refresh_token: str = create_refresh_token(identity=username)

        return jsonify({
            "messages": f"用户登录成功",
            "status": 200,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {"username": username}
        }), 200
    return jsonify({"messages": "用户名或密码错误"}), 401


@app.route("/api/me", methods=["GET"])
@jwt_required()
def get_my_profile_api() -> tuple[jsonify, int]:
    # --- Token知识点：服务器端Token验证流程 ---
    # 当一个请求到达被`@jwt_required()`装饰的端点时，Flask-JWT-Extended会自动执行以下操作：
    # 1. 提取Token: 从预设的位置查找Token。默认情况下，它会查找HTTP请求的`Authorization`头部，
    # 并期望Token的格式为 `Bearer <JWT_STRING>`。Token的查找位置可以通过配置`JWT_TOKEN_LOCATION`来修改。
    # 2. 验证Token类型: 确保这是一个"access"类型的Token（因为`@jwt_required()`默认需要Access Token，
    #    而`@jwt_required(refresh=True)`则需要Refresh Token）
    # 3. 验证签名 (Signature): 使用在Flask应用配置中设置的`JWT_SECRET_KEY`和JWT头部声明的算法(alg)，
    #    来验证Token的签名部分。如果签名无效（说明Token可能被篡改或密钥不匹配），请求将被拒绝。
    # 4. 验证标准声明 (Standard Claims):
    #    - `exp` (Expiration Time): 检查Token是否已过期。如果过期，请求将被拒绝。
    #    - `nbf` (Not Before): 如果存在此声明，检查Token是否已到达其生效时间。
    #    - `iat` (Issued At): 记录Token的签发时间。
    #    - `jti` (JWT ID): 每个Token的唯一标识符，主要用于Token吊销（黑名单机制）。
    # 5. 黑名单检查 (Blocklist Check): 如果应用配置中启用了`JWT_BLACKLIST_ENABLED = True`，
    #    并且定义了`@jwt.token_in_blocklist_loader`回调函数，那么`Flask-JWT-Extended`会调用这个回调，
    #    传入Token的`jti`，以检查该Token是否已被吊销。如果回调返回`True`，请求将被拒绝。
    #
    # 如果上述任何一步验证失败，`Flask-JWT-Extended`会自动返回一个相应的HTTP错误响应，
    # 通常是 `401 Unauthorized` (例如Token缺失、过期、被吊销) 或 `422 Unprocessable Entity` (例如Token格式错误、签名无效)。
    # 开发者可以通过 `@jwt.expired_token_loader`, `@jwt.invalid_token_loader` 等回调来定制这些错误响应的格式。
    # 如果所有验证都通过，则请求被允许进入被装饰的路由函数。

    # 获取通过Token传递的identity (即登录时create_access_token的identity参数)
    current_user_identity: str = get_jwt_identity()

    # (可选) 获取Token 中的所有声明，包括自定义声明
    jwt_claims: dict = get_jwt()

    # 从内存存储中获取用户信息(实际上这里要查询数据库，等待我们学习到数据库章...)
    user_data_from_store = users_in_memory_store.get(current_user_identity)

    # 为了安全，不要直接返回存储中的哈希密码
    # 此处可以构建一个包含安全信息的用户对象返回给前端
    user_profile_data = {
        "username": current_user_identity,
        "login_time": jwt_claims.get("iat"),
        "expiration_time": jwt_claims.get("exp"),
        "token_type": jwt_claims.get("type")
    }

    return jsonify(user_profile_data), 200


@app.route("/api/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)  # 关键：表明此断点需要的是Refresh Token
def refresh_access_token_api() -> tuple[jsonify, int]:
    """
        使用有效的 Refresh Token 获取一个新的 Access Token。
    """
    # --- Token 知识点：Refresh Token 的验证与使用 ---
    # 1. 客户端在请求头 `Authorization: Bearer <refresh_token>` 中发送 Refresh Token。
    # 2. `@jwt_required(refresh=True)` 装饰器会专门验证传入的是否为 Refresh Token，
    #    并检查其签名、有效期等。
    # 3. 如果 Refresh Token 有效，`get_jwt_identity()` 仍然可以提取出用户的身份信息。
    # 4. 服务器基于此身份信息签发一个新的 Access Token。
    #    通常，通过刷新获得的 Access Token 不再标记为 "fresh" (`fresh=False`)。
    # 5. 一般情况下，刷新操作不会同时签发新的 Refresh Token (除非实现了 Refresh Token 轮换策略)。
    current_user_identity: str = get_jwt_identity()

    # 创建新的 Access Token
    new_access_token: str = create_access_token(identity=current_user_identity, fresh=False)

    logger.info(f"用户 '{current_user_identity}' 刷新了 Access Token。")
    return jsonify({
        "messages": f"新的 Access Token 已生成",
        "status": 200,
        "access_token": new_access_token
    }), 200

@app.route("/api/auth/logout", methods=["DELETE"])
@jwt_required()
def logout_user_api() -> tuple[jsonify, int]:
    """
    用户登出，将当前用户的Token添加到黑名单中。
    """
    jti = get_jwt()["jti"]
    TOKEN_BLOCKLIST.add(jti)
    logger.info(f"Token JTI '{jti}' 已添加到黑名单中。")
    return jsonify({"messages": "登出成功，Token已添加到黑名单中。", "status": 200}), 200



if __name__ == '__main__':
    app.run(debug=True)
