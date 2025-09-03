from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from ..core.encryption import password_encryption

Base = declarative_base()


class ToolType(enum.Enum):
    QUERY = "query"
    HTTP = "http"
    CODE = "code"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    roles = Column(String(500), default="", nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

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

    @property
    def roles_list(self) -> list:
        """Get roles as a list."""
        print(f"Getting roles from list: {self.roles}")
        if not self.roles:
            return []
        return [role.strip() for role in self.roles.split(',') if role.strip()]
    
    @roles_list.setter
    def roles_list(self, value: list):
        """Set roles from a list (will be stored as comma-separated string)."""
        print(f"Setting roles from list: {value}")
        if value:
            self.roles = ','.join([role.strip() for role in value if role.strip()])
        else:
            self.roles = ""

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', first_name='{self.first_name}', last_name='{self.last_name}')>"


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
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationship
    tools = relationship("Tool", back_populates="datasource")

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


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    type = Column(Enum(ToolType), nullable=False, default=ToolType.QUERY)
    sql = Column(Text, nullable=False)
    datasource_id = Column(Integer, ForeignKey("datasources.id"), nullable=False)
    parameters = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    # Relationship
    datasource = relationship("Datasource", back_populates="tools")

    def __repr__(self):
        return f"<Tool(id={self.id}, name='{self.name}', type='{self.type.value}', datasource_id={self.datasource_id})>" 