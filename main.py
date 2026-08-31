from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal
import random # YENİ: Piyasa motoru için

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VaultWatches API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def create_dummy_user():
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.email == "test@vault.com").first()
    if not user:
        new_user = models.User(id="koleksiyoner-123", email="test@vault.com", full_name="Ana Kullanıcı")
        db.add(new_user)
        db.commit()
    db.close()

@app.post("/watches/", response_model=schemas.WatchResponse)
def create_watch(watch: schemas.WatchCreate, db: Session = Depends(get_db)):
    db_watch = models.Watch(**watch.model_dump(), user_id="koleksiyoner-123")
    db.add(db_watch)
    db.commit()
    db.refresh(db_watch)
    # Yeni ekleneni geri döndürürken get_watches içindeki motor hesaplasın diye GET'e yönlendirmiş gibi oluyoruz
    # Ama basitlik için burada da varsayılan değerleri ekleyelim:
    return {**db_watch.__dict__, "market_price": float(db_watch.purchase_price), "profit_str": "+ $ 0", "is_loss": False}

# 🔴 YENİ: CANLI PİYASA MOTORU (GET İSTEĞİ)
@app.get("/watches/", response_model=list[schemas.WatchResponse])
def get_watches(db: Session = Depends(get_db)):
    watches = db.query(models.Watch).all()
    result = []
    
    for w in watches:
        # SQLAlchemy objesini sözlüğe (dict) çeviriyoruz
        watch_dict = {
            "id": w.id, "user_id": w.user_id, "brand": w.brand, "model": w.model,
            "reference_number": w.reference_number, "purchase_price": float(w.purchase_price) if w.purchase_price else 0.0,
            "currency": w.currency, "image_url": w.image_url, "notes": w.notes,
            "is_custom_brand": w.is_custom_brand, "created_at": w.created_at,
        }
        
        purchase = watch_dict["purchase_price"]
        brand_up = w.brand.upper()
        
        # Aynı saatin fiyatı sayfayı her yenilediğimizde değişmesin diye saatin ID'sini "tohum(seed)" yapıyoruz
        random.seed(w.id) 
        
        # MARKA BAZLI ALGORİTMA: Lüks markalar değerlenir, sıradanlar değer kaybeder
        if brand_up in ["ROLEX", "PATEK PHILIPPE", "AUDEMARS PIGUET"]:
            multiplier = random.uniform(1.05, 1.30) # %5 ile %30 arası kâr
        elif brand_up in ["OMEGA", "CARTIER", "TUDOR", "Vacheron Constantin"]:
            multiplier = random.uniform(0.95, 1.10) # %5 zarar ile %10 kâr arası
        else:
            multiplier = random.uniform(0.75, 0.95) # %5 ile %25 arası zarar
            
        market_price = round(purchase * multiplier, 2)
        difference = market_price - purchase
        is_loss = difference < 0
        
        sign = "-" if is_loss else "+"
        formatted_diff = "{:,.0f}".format(abs(difference))
        
        watch_dict["market_price"] = market_price
        watch_dict["profit_str"] = f"{sign} $ {formatted_diff}"
        watch_dict["is_loss"] = is_loss
        
        result.append(watch_dict)
        
    return result

@app.put("/watches/{watch_id}")
def update_watch(watch_id: str, watch_update: schemas.WatchCreate, db: Session = Depends(get_db)):
    db_watch = db.query(models.Watch).filter(models.Watch.id == watch_id).first()
    if not db_watch: raise HTTPException(status_code=404, detail="Saat bulunamadı")
    update_data = watch_update.model_dump(exclude_unset=True)
    for key, value in update_data.items(): setattr(db_watch, key, value)
    db.commit()
    db.refresh(db_watch)
    return {**db_watch.__dict__, "market_price": float(db_watch.purchase_price), "profit_str": "+ $ 0", "is_loss": False}

@app.delete("/watches/{watch_id}")
def delete_watch(watch_id: str, db: Session = Depends(get_db)):
    db_watch = db.query(models.Watch).filter(models.Watch.id == watch_id).first()
    if not db_watch: raise HTTPException(status_code=404, detail="Saat bulunamadı")
    db.delete(db_watch)
    db.commit()
    return {"status": "success"}