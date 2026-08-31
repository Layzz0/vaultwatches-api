from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

import models
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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

@app.get("/watches/stats")
def get_watch_stats(db: Session = Depends(get_db)):
    total_watches = db.query(models.Watch).count()
    total_value = db.query(func.sum(models.Watch.price)).scalar() or 0
    
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

@app.get("/watches/")
def get_watches(db: Session = Depends(get_db)):
    return db.query(models.Watch).all()

@app.post("/watches/")
def create_watch(watch: dict, db: Session = Depends(get_db)):
    new_watch = models.Watch(
        brand=watch.get("brand"),
        model=watch.get("model"),
        reference_number=watch.get("reference_number", ""),
        price=watch.get("price", 0.0),
        notes=watch.get("notes", ""),
        image_url=watch.get("image_url", "")
    )
    db.add(new_watch)
    db.commit()
    db.refresh(new_watch)
    return new_watch

@app.delete("/watches/{watch_id}")
def delete_watch(watch_id: int, db: Session = Depends(get_db)):
    watch = db.query(models.Watch).filter(models.Watch.id == watch_id).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Saat bulunamadı")
    
    db.delete(watch)
    db.commit()
    return {"message": "Saat başarıyla silindi"}