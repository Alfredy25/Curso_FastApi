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


class CourseORM(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    lessons: Mapped[list["LessonORM"]] = relationship(
        "LessonORM",
        back_populates="course",
        cascade="all, delete-orphan"
    )


class LessonORM(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)

    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))

    course: Mapped["CourseORM"] = relationship("CourseORM",
        back_populates="lessons"
    )


Base.metadata.create_all(bind=engine) # dev


if __name__ == '__main__':
    with SessionLocal() as session:
        curso = session.get(CourseORM, 2)
        # curso1 = CourseORM(name='FastAPI')
        # curso2 = CourseORM(name='Python')
        #
        # session.add_all([curso1, curso2])
        # session.commit()

        # leccion1 = LessonORM(title='Operadores')
        # leccion2 = LessonORM(title='Flujo de Control')
        #
        # session.add_all([leccion1, leccion2])
        #
        # curso2.lessons.extend([leccion1, leccion2])
        # session.commit()

        # Desde cursos acceder a sus lecciones
        for leccion in curso.lessons:
            print("Leccion: ", leccion.title)

        # Desde leccion acceder a un curso
        # leccion = session.get(LessonORM, 1)
        # print(f"Curso asociado a la leccion {leccion.title} -> ", leccion.course.name)














