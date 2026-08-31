from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid
from database import Base

def generate_uuid():
    return uuid.uuid4().hex

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    watches = relationship("Watch", back_populates="owner", cascade="all, delete-orphan")

class Watch(Base):
    __tablename__ = "watches"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    reference_number = Column(String, default="Bilinmeyen Ref")
    purchase_price = Column(Numeric(12, 2), default=0.00)
    currency = Column(String, default="USD")
    image_url = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    is_custom_brand = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    owner = relationship("User", back_populates="watches")
    market_prices = relationship("MarketPrice", back_populates="watch", cascade="all, delete-orphan")

class MarketPrice(Base):
    __tablename__ = "market_prices"
    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    watch_id = Column(String, ForeignKey("watches.id"), nullable=False)
    current_value = Column(Numeric(12, 2), nullable=False)
    checked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    watch = relationship("Watch", back_populates="market_prices")