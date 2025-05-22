# backend/app/apis/auth_api.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from loguru import logger
from pyexpat.errors import messages

from ..extensions import db  # 从 app.extensions 导入共享的db实例
from ..models.user_model import User  # 导入User模型
from ..models.token_model import TokenBlocklist  # 导入TokenBlocklist模型

# 创建名为'auth_api'的蓝图实例 (已在5.3.2节定义)
auth_bp = Blueprint('auth_api', __name__)


@auth_bp.route('/register', methods=['POST'])
def register() -> tuple[jsonify, int]:
    """
    用户注册API端点。
    接收JSON格式的用户名和密码，创建新用户并存入数据库。
    """
    data: dict | None = request.get_json()
    # TODO (后续章节): 使用Pydantic或Flask-Marshmallow进行更严格和声明式的请求体验证
    if not data or not data.get('username') or not data.get('password'):
        logger.warning("注册请求缺少username或password字段。")
        return jsonify(message="请求体必须包含'username'和'password'字段"), 400

    username: str = data['username'].strip()
    password: str = data['password']

    if not username:
        logger.warning("注册请求中的username为空。")
        return jsonify(message="用户名不能为空"), 400
    if len(password) < 6:
        logger.warning(f"用户 '{username}' 尝试使用过短的密码注册。")
        return jsonify(message="密码长度不能少于6个字符"), 400

    # 使用User模型查询数据库，检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        logger.info(f"注册尝试失败：用户名 '{username}' 已在数据库中存在。")
        return jsonify(message=f"用户名 '{username}' 已被注册"), 409  # HTTP 409 Conflict

    # 创建User模型实例
    new_user = User(username=username)
    new_user.set_password(password)  # 使用User模型内部定义的set_password方法进行密码哈希

    try:
        db.session.add(new_user)  # 将新用户对象添加到SQLAlchemy的数据库会话中
        db.session.commit()  # 提交会话，将更改实际写入数据库
        logger.info(f"用户 '{username}' (ID: {new_user.id}) 注册成功并存入数据库。")
        return jsonify(message=f"用户 '{username}' 注册成功，请登录。"), 201  # HTTP 201 Created
    except Exception as e:
        db.session.rollback()  # 如果在提交过程中发生任何数据库错误，回滚事务
        logger.error(f"注册用户 '{username}' 时数据库操作失败: {e}")
        return jsonify(message="注册服务内部错误，请稍后再试。"), 500


@auth_bp.route('/login', methods=['POST'])
def login() -> tuple[jsonify, int]:
    """
    用户登录API端点。
    验证用户凭证，如果成功，则签发Access Token和Refresh Token。
    """
    data: dict | None = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        logger.warning("登录请求缺少username或password字段。")
        return jsonify(message="请求体必须包含'username'和'password'字段"), 400
    username: str = data['username'].strip()
    password: str = data['password']

    user: User | None = User.query.filter_by(username=username).first()

    if user and user.check_password(password):  # 使用User模型内部定义的check_password方法进行密码验证
        if not user.is_active:
            logger.warning(f"已禁用账户尝试登录: '{username}' (ID: {user.id})")
            return jsonify(message="账户已被禁用，请联系管理员"), 403

        user_roles = ["user"]  # 简化示例，实际应从数据库获取
        additional_claims_data = {"roles": user_roles}
        # 生成Access Token和Refresh Token

        # 回顾：create_access_token:
        # (1):identity: 标识用户的唯一标识符，通常是用户ID。
        # (2):fresh: 布尔值，用于标记Access Token是否为"fresh"。
        # (3):additional_claims_data: 可选的额外声明数据，通常用于存储用户角色等信息。
        access_token = create_access_token(
            identity=user.username,
            fresh=True,
            additional_claims=additional_claims_data
        )

        refresh_token: str = create_refresh_token(
            identity=user.username,
            additional_claims=additional_claims_data
        )

        logger.info(f"用户 '{username}' (ID: {user.id}) 登录成功。")
        return jsonify(
            message=f"用户 '{username}' 登录成功。",
            access_token=access_token,
            refresh_token=refresh_token,
            user={"id": user.id, "username": user.username, "roles": user_roles}
        ), 200
    logger.warning(f"用户 '{username}' 尝试登录失败：用户名或密码无效。")
    return jsonify(message="用户名或密码无效。"), 401


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token_api() -> tuple[jsonify, int]:
    current_user_id: int = get_jwt_identity()
    user: User | None = User.query.filter_by(id=current_user_id, is_active=True).first()
    if not user:
        logger.warning(f"Refresh Token无效或用户(ID: {current_user_id})不存在/已禁用。")
        return jsonify(message="Refresh Token无效或用户状态异常。"), 401

    user_roles = ["user"]
    additional_claims_data = {"roles": user_roles}
    new_access_token: str = create_access_token(
        identity=current_user_id,
        fresh=False,
        additional_claims=additional_claims_data
    )
    logger.info(f"用户ID '{current_user_id}' 的Access Token已刷新。")
    return jsonify(access_token=new_access_token), 200


@auth_bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout_access_api() -> tuple[jsonify, int]:
    jwt_payload: dict = get_jwt()
    jti: str = jwt_payload["jti"]
    token_type: str = jwt_payload.get("type", "access")
    user_identity: str = str(get_jwt_identity())

    if TokenBlocklist.query.filter_by(jti=jti).one_or_none():
        logger.info(f"Access Token JTI '{jti}' 已在黑名单中。")
        return jsonify(message="您已登出。"), 200

    try:
        blocked_token = TokenBlocklist(jti=jti, token_type=token_type, user_identity=user_identity)
        db.session.add(blocked_token)
        db.session.commit()
        logger.info(f"Access Token JTI '{jti}' for user '{user_identity}' 已加入数据库黑名单。")
        return jsonify(message="Access Token已成功吊销，安全登出。"), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"吊销Access Token JTI '{jti}' 时数据库操作失败: {e}")
        return jsonify(message="登出过程中发生服务器内部错误。"), 500

