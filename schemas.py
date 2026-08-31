from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WatchBase(BaseModel):
    brand: str
    model: str
    reference_number: Optional[str] = "Bilinmeyen Ref"
    purchase_price: Optional[float] = 0.0
    currency: Optional[str] = "USD"
    image_url: Optional[str] = None
    notes: Optional[str] = None
    is_custom_brand: Optional[bool] = False

class WatchCreate(WatchBase):
    pass

class WatchResponse(WatchBase):
    id: str
    user_id: str
    created_at: datetime
    
    # YENİ: Canlı Piyasa Motorundan Gelecek Veriler
    market_price: Optional[float] = 0.0
    profit_str: Optional[str] = "$ 0"
    is_loss: Optional[bool] = False

    class Config:
        from_attributes = True