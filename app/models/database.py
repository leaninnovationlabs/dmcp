from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from ..core.encryption import password_encryption

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    roles = Column(String(500), default="", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

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
        return [role.strip() for role in self.roles.split(",") if role.strip()]

    @roles_list.setter
    def roles_list(self, value: list):
        """Set roles from a list (will be stored as comma-separated string)."""
        print(f"Setting roles from list: {value}")
        if value:
            self.roles = ",".join([role.strip() for role in value if role.strip()])
        else:
            self.roles = ""

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}',last_name='{self.last_name}', roles='{self.roles}')>"


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
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

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


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    type = Column(String(50), nullable=False, default='query')
    sql = Column(Text, nullable=False)
    datasource_id = Column(Integer, ForeignKey("datasources.id"), nullable=False)
    parameters = Column(JSON, default=[])
    tags = Column(JSON, default=lambda: [])
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationship
    datasource = relationship("Datasource", back_populates="tools")

    def __repr__(self):
        return f"<Tool(id={self.id}, name='{self.name}', type='{self.type}', datasource_id={self.datasource_id})>"         
