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

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class AuthorORM(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Relacion Muchos
    posts: Mapped[List[PostORM]] = relationship(back_populates="author")

class TagORM(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, index=True)

    posts: Mapped[List["PostORM"]] = relationship(
        secondary=post_tags,
        back_populates="tags",
        lazy="selectin",
    )


class PostORM(Base):
    __tablename__ = "posts"
    __table_args__ = (
        UniqueConstraint("title", "content", name="unique_post_title_content"),
        CheckConstraint("trim(title) <> ''", name="check_title_not_empty"),
        Index("icx_id_title", "id", "title")
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True, unique=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    # Relacion uno
    author_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("authors.id"))
    author: Mapped[Optional["AuthorORM"]] = relationship(back_populates="posts")

    tags: Mapped[List[TagORM]] = relationship(
        secondary=post_tags,
        back_populates="posts",
        lazy="selectin",
        passive_deletes=True
    )

Base.metadata.create_all(bind=engine) # dev

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Mini Blog")

class Tag(BaseModel):
    name: str = Field(..., min_length=2, max_length=30, description="Nombre de la etiqueta")


class Author(BaseModel):
    name: str
    email: EmailStr


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list) # Crea una lista por cada objeto que se crea en el programa
    author: Optional[Author] = None


class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Titulo del post (mínimo 3 caracteres, máximo 100)",
        examples=["Mi primer post con FastAPI"]
    )
    content: Optional[str] = Field(
        default="Contenido no disponible",
        min_length=10,
        description="Contenido del post (mínimo 10 caracteres)",
        examples=["Este es un contenido válido porque tiene 10 caracteres o más"]
    )
    tags: List[Tag] = Field(default_factory=list) # []
    author: Optional[Author] = None

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("El título no puede contener la palabra: 'spam'")
        return value


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None


class PostPublic(PostBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class PostSummary(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)

class PaginatedPost(BaseModel):
    page: int
    per_page: int  # limit
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items: List[PostPublic]


@app.get("/")
def home():
    return {'message': 'Bienvenidos a Mini Blog por Devtalles'}


@app.get("/posts", response_model=PaginatedPost)
def list_posts(text: Optional[str] = Query(default=None, deprecated=True, description="Parametro obsoleto usa 'query o seach' en su lugar."),
               query: Optional[str] = Query(default=None, description="Texto para buscar por título", alias="search", min_length=3, max_length=50, pattern=r"^[a-zA-Z]+$"),
               per_page: int = Query(10, ge=1, le=50, description="Número de resultados (1-50)"),
               page: int = Query(default=1, ge=1, description="Número de página (>=1)"),
               order_by: Literal["id", "title"] = Query("id", description="Campo de orden"),
               direction: Literal["desc", "asc"] = Query("asc", description="Dirección de orden"),
               db: Session = Depends(get_db)):


    results = select(PostORM)
    query = query or text
    if query:
        results = results.where(PostORM.title.ilike(f"%{query}%"))
        # results =  [post for post in results
        #             if query.lower() in post["title"].lower()]

    total = db.scalar(select(func.count()).select_from(results.subquery())) or 0
    total_pages = ceil(total/per_page) if total > 0 else 0

    current_page = 1 if total_pages == 0 else min(page, total_pages)
    if order_by == "id":
        order_col = PostORM.id
    else:
        order_col = func.lower(PostORM.title)

    results = results.order_by(
        order_col.asc() if direction == "asc" else order_col.desc())

    # results = sorted(results, key= lambda post: post[order_by], reverse=(direction == "desc"))

    if total_pages == 0:
        items: List[PostORM] = []
    else:
        start = (current_page - 1) * per_page
        # items = db.execute(results.limit(per_page).offset(start)).scalars().all()
        items = list(db.scalars(results.limit(per_page).offset(start)).all())
    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False

    return PaginatedPost(page = current_page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         order_by=order_by,
                         direction=direction,
                         search=query,
                         items= [PostPublic.model_validate(item) for item in items])


@app.get("/posts/by-tags", response_model=List[PostPublic])
def filter_by_tags(tags: List[str] = Query(..., min_length=2, description="Una o mas etiquetas Ejemplo: ?tags=python&tags=fastapi")):
    tags_lower = [tag.lower() for tag in tags]
    return [
        post for post in BLOG_POST
        if any(
            tag["name"].lower() in tags_lower
            for tag in post.get('tags', [])
        )
    ]

@app.get("/posts/{post_id}", response_model=Union[PostPublic, PostSummary], response_description="Post encontrado")
def get_post(post_id: int = Path(..., ge=1, title="ID del post", description="Identificador entero del post. Debe se mayor o igual a 1", examples=[1]),
             include_content: bool = Query(default=True, description="Incluir o no el contenido"),
             db: Session = Depends(get_db)):

    stmt = select(PostORM).where(PostORM.id == post_id)
    post = db.execute(stmt).scalar_one_or_none()

    # post = db.get(PostORM, post_id) # solo cuando es una primary key
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")

    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)


@app.post("/posts", response_model=PostPublic, response_description="Post creado (OK)", status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = PostORM(title=post.title, content=post.content)
    try:
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post
    except IntegrityError as e:
        db.rollback()
        print(e.orig)
        print(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{"titulo vacio" if str(e.orig).find("check_title_not_empty") else "El titulo ya existe o el contenido"}")

    except SQLAlchemyError as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear post")



@app.put("/posts/{post_id}", response_model=PostPublic, response_description="Post actualizado",
         response_model_exclude_none=True)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    post_find = db.get(PostORM, post_id)
    if not post_find:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")

    try:
        updates = data.model_dump(exclude_none=True) # Exclude_unset quita los valores None
        for key, value in updates.items():
            setattr(post_find, key, value)

        db.add(post_find)
        db.commit()
        db.refresh(post_find)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar")


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT, response_description="Post eliminado")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post_find = db.get(PostORM, post_id)
    if not post_find:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")
    try:
        db.delete(post_find)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar")
