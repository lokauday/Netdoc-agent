# ===============================================================
#  NetDoc AI — DATABASE MODELS (PostgreSQL + SQLAlchemy ORM)
# ===============================================================

import os
import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime,
    ForeignKey, Text
)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# ---------------------------------------------------------------
# DATABASE URL
# ---------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set in environment variables.")

# ---------------------------------------------------------------
# ENGINE + SESSION
# ---------------------------------------------------------------
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ===============================================================
#  ORGANIZATION TABLE
# ===============================================================
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    org_name = Column(String, unique=True, nullable=False)

    # Billing
    plan = Column(String, default="free")                
    stripe_customer_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization")
    uploads = relationship("Upload", back_populates="organization")
    audits = relationship("AuditReport", back_populates="organization")


# ===============================================================
#  USER TABLE
# ===============================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    org_id = Column(Integer, ForeignKey("organizations.id"))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Admin flag
    is_admin = Column(Integer, default=0)

    # Billing
    stripe_subscription_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    uploads = relationship("Upload", back_populates="user")
    audits = relationship("AuditReport", back_populates="user")


# ===============================================================
#  UPLOAD TABLE
# ===============================================================
class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)

    org_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    filename = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="uploads")
    organization = relationship("Organization", back_populates="uploads")


# ===============================================================
#  AUDIT REPORT TABLE
# ===============================================================
class AuditReport(Base):
    __tablename__ = "audit_reports"

    id = Column(Integer, primary_key=True, index=True)

    org_id = Column(Integer, ForeignKey("organizations.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    audit_json = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="audits")
    organization = relationship("Organization", back_populates="audits")


# ===============================================================
#  INIT DB
# ===============================================================
def init_db():
    print("📌 Initializing database…")

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create default org if none exists
    org = db.query(Organization).first()
    if not org:
        org = Organization(org_name="DefaultOrg", plan="free")
        db.add(org)
        db.commit()

    db.close()
    print("✔ Tables ready.")
