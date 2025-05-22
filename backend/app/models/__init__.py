# backend/app/models/__init__.py
from .user_model import User
from .token_model import TokenBlocklist

# (可选) __all__ 变量可以定义当使用 from .models import * 时导出的名称
__all__ = ['User', 'TokenBlocklist']