# backend/app/apis/user_api.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from loguru import logger
from datetime import datetime, timezone

from ..models.user_model import User # 导入User模型

user_bp = Blueprint('user_api', __name__) # 创建蓝图实例

@user_bp.route('/me', methods=['GET']) # 当蓝图以 url_prefix='/api' 注册时，此路由是 /api/me
@jwt_required() 
def get_my_profile() -> tuple[jsonify, int]:
    """
    获取当前认证用户的个人资料。
    需要有效的Access Token。
    """
    # 获取通过Token传递的identity (即登录时create_access_token的identity参数)
    current_user_identity: str = get_jwt_identity()


    # (可选) 获取Token 中的所有声明，包括自定义声明
    jwt_claims: dict = get_jwt()

    # 从数据库中获取用户信息
    user: User | None = User.query.filter_by(username=current_user_identity).first()
    
    if not user:
        logger.warning(f"受保护API /me：找不到用户ID为 '{current_user_identity}' 的用户（Token有效但用户可能已被删除）。")
        return jsonify(message="找不到用户资料。"), 404

    # 为了安全，不要直接返回存储中的哈希密码
    # 此处可以构建一个包含安全信息的用户对象返回给前端
    user_profile_data = {
        "username": current_user_identity,
        "login_time": jwt_claims.get("iat"),
        "expiration_time": jwt_claims.get("exp"),
        "token_type": jwt_claims.get("type")
    }

    return jsonify(user_profile_data), 200