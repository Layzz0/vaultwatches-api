from sqlalchemy import Column, Integer, String, Float, Text
from database import Base

class Watch(Base):
    __tablename__ = "watches"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    reference_number = Column(String, default="")
    price = Column(Float, default=0.0)
    notes = Column(Text, default="")
    image_url = Column(String, default="")