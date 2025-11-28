# ============================================================
#  NetDoc AI — Enterprise Edition
#  database.py (FINAL FULL VERSION)
# ============================================================

import os
import json
import streamlit as st
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String,
    Text, Boolean, ForeignKey, DateTime
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from dotenv import load_dotenv
import bcrypt

# ------------------------------------------------------------
# LOAD SECRETS + .ENV
# ------------------------------------------------------------
load_dotenv()

# Prefer local DATABASE_URL → fallback to Streamlit secrets
DATABASE_URL = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception(
        "❌ DATABASE_URL missing! Add it to Streamlit Secrets or .env"
    )

# ------------------------------------------------------------
# CREATE ENGINE
# ------------------------------------------------------------
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
    role = Column(String, default="user")   # user/admin
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
#  UPLOADED CONFIGS
# ============================================================
class UploadedConfig(Base):
    __tablename__ = "uploaded_configs"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    file_name = Column(String)
    content = Column(Text)
    parsed_json = Column(Text)  # store JSON string

    organization = relationship("Organization", back_populates="uploads")


# ============================================================
#  AUDIT REPORTS
# ============================================================
class AuditReport(Base):
    __tablename__ = "audit_reports"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    title = Column(String)
    result = Column(Text)  # JSON dump
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="audits")


# ============================================================
#  ACTIVITY LOGS (metadata FIXED → meta_json)
# ============================================================
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey("organizations.id"))
    event = Column(String)
    meta_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="logs")


# ============================================================
#  DATABASE INITIALIZER + DEFAULT ADMIN
# ============================================================
def init_db():
    print("📢 Creating tables...")
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


# ============================================================
#  JSON HELPERS
# ============================================================
def to_json(obj):
    return json.dumps(obj, indent=2)

def from_json(txt):
    try:
        return json.loads(txt)
    except:
        return {}
