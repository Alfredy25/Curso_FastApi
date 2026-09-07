from datetime import datetime, timezone
import os

from fastapi import FastAPI, Query, Body, HTTPException, Path, status, Depends
from pydantic import BaseModel, Field, field_validator, EmailStr, ConfigDict
from typing import Optional, List, Union, Literal
from math import ceil
from sqlalchemy import create_engine, Integer, String, Text, DateTime, select, func, UniqueConstraint, CheckConstraint, Index, ForeignKey, Table, Column
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")
print("Conectado a: ", DATABASE_URL)

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=True, future=True, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)

class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    profile: Mapped["ProfileORM"] = relationship("ProfileORM", back_populates="user")


class ProfileORM(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True
    )

    user: Mapped["UserORM"] = relationship(back_populates = "profile")


Base.metadata.create_all(bind=engine) # dev


if __name__ == '__main__':
    with SessionLocal() as session:
        user1 = session.get(UserORM, 1)
        # user2 = UserORM(name="Gabriel")
        #
        # session.add_all([user1, user2])
        # session.commit()

        perfil1 = ProfileORM(role="Admin", user=user1)
        # perfil2 = ProfileORM(role="Operador")
        # perfil3 = ProfileORM(role="Cliente")

        session.add(perfil1)
        # session.add_all([perfil1, perfil2, perfil3])
        session.commit()
        session.refresh(perfil1)

        print(f"perfil de user {user1.name} perfil: ", user1.profile.role)
        print(f'usuario que pertenece al perfil {perfil1.role}', perfil1.user.name)





















