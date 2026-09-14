from typing import List, Literal, Optional, Union
from fastapi import APIRouter, Query, Depends, HTTPException, Path, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.db import get_db
from .schemas import (PostPublic, PaginatedPost, PostCreate, PostUpdate, PostSummary)
from .repository import PostRepository
from sqlalchemy.orm import Session
from math import ceil

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("", response_model=PaginatedPost)
def list_posts(text: Optional[str] = Query(default=None, deprecated=True, description="Parametro obsoleto usa 'query o seach' en su lugar."),
               query: Optional[str] = Query(default=None, description="Texto para buscar por título", alias="search", min_length=3, max_length=50, pattern=r"^[a-zA-Z]+$"),
               per_page: int = Query(10, ge=1, le=50, description="Número de resultados (1-50)"),
               page: int = Query(default=1, ge=1, description="Número de página (>=1)"),
               order_by: Literal["id", "title"] = Query("id", description="Campo de orden"),
               direction: Literal["desc", "asc"] = Query("asc", description="Dirección de orden"),
               db: Session = Depends(get_db)):

    repository = PostRepository(db=db)
    query = query or text
    total, items = repository.search(query, order_by, direction, page, per_page)
    total_pages = ceil(total / per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page, total_pages)

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

@router.get("/by-tags", response_model=List[PostPublic])
def filter_by_tags(tags: List[str] = Query(..., min_length=1, description="Una o mas etiquetas Ejemplo: ?tags=python&tags=fastapi"),
                   db: Session = Depends(get_db)):
    repository = PostRepository(db=db)
    return repository.by_tags(tags)

@router.get("/{post_id}", response_model=Union[PostPublic, PostSummary], response_description="Post encontrado")
def get_post(post_id: int = Path(..., ge=1, title="ID del post", description="Identificador entero del post. Debe se mayor o igual a 1", examples=[1]),
             include_content: bool = Query(default=True, description="Incluir o no el contenido"),
             db: Session = Depends(get_db)):

    repository = PostRepository(db=db)
    post = repository.get(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")

    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)


@router.post("", response_model=PostPublic, response_description="Post creado (OK)", status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    repository = PostRepository(db=db)

    try:
        post = repository.create_post(
            title=post.title,
            content=post.content,
            author= (post.author.model_dump() if post.author else None),
            tags = [tag.model_dump() for tag in post.tags]
        )
        db.commit()
        db.refresh(post)
        return post
    except IntegrityError as e:
        db.rollback()
        print(e.orig)
        print(e)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"{"titulo vacio" if str(e.orig).find("check_title_not_empty") else "El titulo ya existe o el contenido"}")

    except SQLAlchemyError as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear post")

@router.put("/{post_id}", response_model=PostPublic, response_description="Post actualizado",
         response_model_exclude_none=True)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db)):
    repository = PostRepository(db=db)
    post = repository.get(post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")

    try:
        updates = data.model_dump(exclude_unset=True)
        post = repository.update_post(post=post, updates=updates)
        db.commit()
        db.refresh(post)
        return post
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el post")


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT, response_description="Post eliminado")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    repository = PostRepository(db=db)
    post = repository.get(post_id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post no encontrado")
    try:
        repository.delete_post(post)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar post")
