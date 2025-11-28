# ============================================================
#  NetDoc AI — Enterprise Edition
#  database.py (FINAL, 100% FIXED)
# ============================================================

import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String,
    Text, Boolean, ForeignKey, DateTime
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from dotenv import load_dotenv
import bcrypt

# ------------------------------------------------------------
# Load .env
# ------------------------------------------------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


# ============================================================
#  ORGANIZATION MODEL
# ============================================================
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    org_name = Column(String, nullable=False)

    users = relationship("User", back_populates="organization")
    logs = relationship("ActivityLog", back_populates="organization")
    keys = relationship("APIKey", back_populates="organization")
    uploads = relationship("UploadedConfig", back_populates="organization")
    audits = relationship("AuditReport", back_populates="organization")
    billing = relationship("Billing", uselist=False, back_populates="organization")


# ============================================================
#  USER MODEL
# ============================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    role = Column(String, default="user")     # user / admin
    is_admin = Column(Boolean, default=False)

    organization = relationship("Organization", back_populates="users")


# ============================================================
#  BILLING
# ============================================================
class Billing(Base):
    __tablename__ = "billing"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    plan = Column(String, default="enterprise")
    status = Column(String, default="active")

    organization = relationship("Organization", back_populates="billing")


# ============================================================
#  API KEYS
# ============================================================
class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    key_hash = Column(String, nullable=False)
    label = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="keys")


# ============================================================
#  UPLOADED CONFIGS (JSONB FIXED)
# ============================================================
class UploadedConfig(Base):
    __tablename__ = "uploaded_configs"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    file_name = Column(String)
    content = Column(Text)

    parsed_json = Column(JSONB)  # <-- FIXED (was Text)

    organization = relationship("Organization", back_populates="uploads")


# ============================================================
#  AUDIT REPORTS
# ============================================================
class AuditReport(Base):
    __tablename__ = "audit_reports"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    title = Column(String)
    result = Column(JSONB)  # <-- also JSONB if storing dict

    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="audits")


# ============================================================
#  ACTIVITY LOGS  (metadata FIXED → meta_json)
# ============================================================
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    event = Column(String)

    meta_json = Column(JSONB)   # <-- FIXED

    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="logs")


# ============================================================
#  INITIALIZE DB + DEFAULT ADMIN
# ============================================================
def init_db():
    print("📢 Creating tables...")
    Base.metadata.drop_all(bind=engine)     # <-- CLEAN RESET
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    ADMIN_EMAIL = "lokauday456@gmail.com"
    ADMIN_PASS = "Bittu369$"

    existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()

    if not existing:
        print("🛠 Creating default organization...")
        org = Organization(org_name="NetDoc AI Enterprise")
        db.add(org)
        db.commit()
        db.refresh(org)

        print("🛠 Creating admin user...")
        hashed = bcrypt.hashpw(ADMIN_PASS.encode(), bcrypt.gensalt()).decode()

        admin = User(
            org_id=org.id,
            email=ADMIN_EMAIL,
            password_hash=hashed,
            role="admin",
            is_admin=True
        )
        db.add(admin)
        db.commit()

        print("🎉 Admin user created!")
    else:
        print("✔ Admin user already exists.")

    db.close()
