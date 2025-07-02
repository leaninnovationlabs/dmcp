from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.encryption import password_encryption

Base = declarative_base()


class Datasource(Base):
    __tablename__ = "datasources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    database_type = Column(String(50), nullable=False)
    host = Column(String(255))
    port = Column(Integer)
    database = Column(String(255), nullable=False)
    username = Column(String(255))
    password = Column(String(255))
    connection_string = Column(Text)
    ssl_mode = Column(String(50))
    additional_params = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    queries = relationship("Query", back_populates="datasource")

    @property
    def decrypted_password(self) -> str:
        """Get the decrypted password."""
        if not self.password:
            return ""
        return password_encryption.decrypt_password(self.password)
    
    @decrypted_password.setter
    def decrypted_password(self, value: str):
        """Set the password (will be encrypted before storage)."""
        if value:
            self.password = password_encryption.encrypt_password(value)
        else:
            self.password = ""

    def __repr__(self):
        return f"<Datasource(id={self.id}, name='{self.name}', type='{self.database_type}')>"


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    sql = Column(Text, nullable=False)
    datasource_id = Column(Integer, ForeignKey("datasources.id"), nullable=False)
    parameters = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    datasource = relationship("Datasource", back_populates="queries")

    def __repr__(self):
        return f"<Query(id={self.id}, name='{self.name}', datasource_id={self.datasource_id})>" 