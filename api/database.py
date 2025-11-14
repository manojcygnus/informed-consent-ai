"""
Database models and schema for Free Consent Management System
Uses SQLite with SQLAlchemy ORM
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import bcrypt

Base = declarative_base()


class Patient(Base):
    """Patient authentication and profile"""
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    patient_name = Column(String(255), nullable=False)
    default_password = Column(String(100))  # For reference only
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to consents
    consents = relationship("Consent", back_populates="patient")

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Verify password"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


class Consent(Base):
    """Consent form raw data"""
    __tablename__ = 'consents'

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    full_text = Column(Text, nullable=False)
    ai_analysis_json = Column(Text)  # JSON string
    processed_timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship
    patient = relationship("Patient", back_populates="consents")
    entity_index = relationship("EntityIndex", back_populates="consent", uselist=False)


class EntityIndex(Base):
    """Structured, searchable consent data"""
    __tablename__ = 'entity_index'

    id = Column(Integer, primary_key=True)
    consent_id = Column(Integer, ForeignKey('consents.id'), nullable=False, unique=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False, index=True)

    # Patient info
    patient_name = Column(String(255))
    patient_email = Column(String(255), index=True)
    patient_dob = Column(String(50))

    # Medical info
    doctor_name = Column(String(255))
    procedure = Column(String(500))
    procedure_date = Column(String(50))

    # Consent details
    consented_items = Column(Text)  # JSON array as string
    declined_items = Column(Text)   # JSON array as string
    summary = Column(Text)

    # Search optimization
    search_terms = Column(Text)  # Space-separated search terms
    processed_timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    consent = relationship("Consent", back_populates="entity_index")


class Session(Base):
    """User sessions for authentication"""
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)


class DatabaseManager:
    """Database connection and session management"""

    def __init__(self, db_path='./data/consent_system.db'):
        """Initialize database connection"""
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else 'data', exist_ok=True)
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def init_db(self):
        """Initialize/reset database"""
        Base.metadata.create_all(self.engine)
        print("Database initialized successfully!")


# Initialize database
def init_database(db_path='./data/consent_system.db'):
    """Initialize database with schema"""
    db_manager = DatabaseManager(db_path)
    db_manager.init_db()
    return db_manager


if __name__ == '__main__':
    # Test database creation
    print("Creating database schema...")
    init_database()
    print("Done!")
