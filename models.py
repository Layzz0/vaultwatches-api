from sqlalchemy import Column, Integer, String, Float
from database import Base

class Watch(Base):
    __tablename__ = "watches"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    price = Column(Float, default=0.0)