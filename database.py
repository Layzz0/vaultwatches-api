from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# 🔴 BURAYA KENDİ SUPABASE LİNKİNİ YAPIŞTIR
# Önemli: Kopyaladığın linkteki [YOUR-PASSWORD] kısmını silip kendi şifreni yaz.
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:[YOUR-PASSWORD]@db.oiwvoqkuyvgmcpqnxwvh.supabase.co:5432/postgres"

# SQLite'a özel ayarları kaldırdık, saf PostgreSQL motorunu kuruyoruz
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()