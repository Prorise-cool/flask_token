# backend/app/models/user_model.py
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db  # 导入db实例
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash  # 用于密码操作


class User(db.Model):
    __tablename__ = 'users'  # 数据库中的表名

    # 定义表列
    id: Mapped[int] = mapped_column(primary_key=True, doc="用户唯一ID")
    username: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False, index=True, doc="用户名，唯一且不能为空")
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=True, index=True, doc="用户邮箱，唯一但可为空")  # 邮箱可以设为可选
    password_hash: Mapped[str] = mapped_column(db.String(255), nullable=False, doc="存储哈希后的密码")

    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(timezone.utc),
                                                 doc="记录创建时间")
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(timezone.utc),
                                                 onupdate=lambda: datetime.now(timezone.utc), doc="记录最后更新时间")
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False, doc="用户是否激活状态")

    # (可选) 定义模型方法
    def set_password(self, password: str) -> None:
        """
        设置用户密码，自动进行哈希处理。
        :param password: 明文密码字符串。
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        验证提供的密码是否与存储的哈希密码匹配。
        :param password: 需要验证的明文密码。
        :return: 如果密码匹配则为True，否则为False。
        """
        return check_password_hash(self.password_hash, password)


    def __repr__(self) -> str:
        # 对象的字符串表示，方便调试
        return f"<User id={self.id}, username='{self.username}'>"

