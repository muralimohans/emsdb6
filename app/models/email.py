from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class EmailValidation(Base):
    __tablename__ = "email_validations"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    valid_syntax = Column(Boolean, default=False)       # ✅ Boolean
    domain_exists = Column(Boolean, default=False)      # ✅ Boolean
    mx_exists = Column(Boolean, default=False)          # ✅ Boolean
    smtp_ok = Column(Boolean, default=False)            # ✅ Boolean
    status = Column(String, default="")
    score = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="validations")