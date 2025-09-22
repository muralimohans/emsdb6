from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic contact info
    name = Column(String, nullable=True)
    title = Column(String, nullable=True)
    email = Column(String, index=True, nullable=True)
    phone = Column(String, nullable=True)

    # Company info
    company_name = Column(String, nullable=True)
    location = Column(String, nullable=True)

    # Metadata
    source = Column(String, nullable=True)
    email_valid = Column(Boolean, default=False)
    phone_valid = Column(Boolean, default=False)
