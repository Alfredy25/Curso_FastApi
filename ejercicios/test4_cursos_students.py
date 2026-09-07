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


enrollments = Table("enrollments",
                    Base.metadata,
                    Column("student_id", ForeignKey("students.id")),
                    Column("course_id", ForeignKey("courses.id"))
                    )

class StudentORM(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_student = mapped_column(String(50), nullable=False)

    courses: Mapped[list["CourseORM"]] = relationship(secondary=enrollments, back_populates="students", lazy="selectin")

class CourseORM(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]

    lessons: Mapped[list[LessonORM]] = relationship()
    students: Mapped[list[StudentORM]] = relationship(secondary=enrollments, back_populates="courses")


class LessonORM(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]

    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))


Base.metadata.create_all(bind=engine) # dev


if __name__ == '__main__':
    with SessionLocal() as session:
        # Creamos cursos
        curso = session.get(CourseORM, 1)
        curso2 = session.get(CourseORM, 2)

        # Creamos un studiante
        student1 = StudentORM(name_student="pancho")

        student1.courses.extend([curso, curso2])
        session.add(student1)
        session.commit()










