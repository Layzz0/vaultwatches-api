from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

# Kendi dosyalarından importlar (Eğer schemas.py yoksa POST kısmını kendine göre düzeltirsin)
import models
from database import SessionLocal, engine

# Veritabanı tablolarını Supabase'de oluşturur
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mobil uygulamanın API'ye sorunsuz bağlanması için CORS izni
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Veritabanı bağlantısını sağlayan fonksiyon
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------
# 1. İSTATİSTİK ENDPOINT'İ (Özel endpoint'ler her zaman en üstte olmalıdır)
# ---------------------------------------------------------
@app.get("/watches/stats")
def get_watch_stats(db: Session = Depends(get_db)):
    # Toplam saat sayısı
    total_watches = db.query(models.Watch).count()
    
    # Toplam değer
    total_value = db.query(func.sum(models.Watch.price)).scalar() or 0
    
    # Markalara göre gruplama
    brand_stats = db.query(
        models.Watch.brand, 
        func.count(models.Watch.id)
    ).group_by(models.Watch.brand).all()
    
    brands_formatted = [{"brand": b[0], "count": b[1]} for b in brand_stats]
    
    return {
        "total_watches": total_watches,
        "total_value": total_value,
        "brand_distribution": brands_formatted
    }

# ---------------------------------------------------------
# 2. STANDART ENDPOINT'LER (Listeleme, Ekleme, Silme)
# ---------------------------------------------------------

# Tüm saatleri listele
@app.get("/watches/")
def get_watches(db: Session = Depends(get_db)):
    watches = db.query(models.Watch).all()
    return watches

# Yeni saat ekle (Eğer schemas.py kullanmıyorsan request body'i kendi yapına göre ayarla)
@app.post("/watches/")
def create_watch(watch: dict, db: Session = Depends(get_db)):
    new_watch = models.Watch(
        brand=watch.get("brand"),
        model=watch.get("model"),
        price=watch.get("price"),
        # Eğer başka sütunların varsa buraya ekle (örn: image_url=watch.get("image_url"))
    )
    db.add(new_watch)
    db.commit()
    db.refresh(new_watch)
    return new_watch

# Saat sil
@app.delete("/watches/{watch_id}")
def delete_watch(watch_id: int, db: Session = Depends(get_db)):
    watch = db.query(models.Watch).filter(models.Watch.id == watch_id).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Saat bulunamadı")
    
    db.delete(watch)
    db.commit()
    return {"message": "Saat başarıyla silindi"}