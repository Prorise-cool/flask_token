# backend/app/models/token_model.py
from sqlalchemy.orm import Mapped, mapped_column

from ..extensions import db
from datetime import datetime, timezone


class TokenBlocklist(db.Model):
    __tablename__ = 'token_blocklist'  # 数据库中的表名

    id: Mapped[int] = mapped_column(primary_key=True, doc="令牌唯一ID")
    jti: Mapped[str] = mapped_column(db.String(36), nullable=False, index=True, doc="JWT的唯一标识符")
    token_type: Mapped[str] = mapped_column(db.String(10), nullable=False, doc="被吊销Token的类型 (access或refresh)")
    user_identity: Mapped[str] = mapped_column(db.String(120), nullable=False, doc="与此JTI关联的用户身份")
    revoked_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=True,
                                                 doc="Token令牌吊销时间",
                                                 default=lambda: datetime.now(timezone.utc),

                                                 )

    def __repr__(self) -> str:
        return f"<TokenBlocklist jti='{self.jti}', user='{self.user_identity}'>"
