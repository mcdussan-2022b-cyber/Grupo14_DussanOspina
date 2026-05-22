#!/usr/bin/env python3
"""
Modelos ORM y conexión PostgreSQL
CORHUILA | Ingeniería de Sistemas | Minería de Datos 2026
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String,
    Float, Boolean, DateTime, Text, ForeignKey, Index
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

load_dotenv()

DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = os.getenv("DB_PORT",     "5433")
DB_USER     = os.getenv("DB_USER",     "etl_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "etl2026")
DB_NAME     = os.getenv("DB_NAME",     "jsonplaceholder_etl")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine       = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()


def test_connection():
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        print("✅ Conexión a PostgreSQL exitosa")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


class Usuario(Base):
    __tablename__ = "usuarios"

    id               = Column(Integer, primary_key=True)
    nombre           = Column(String(200), nullable=False)
    username         = Column(String(100), unique=True, nullable=False, index=True)
    email            = Column(String(200), unique=True, nullable=False)
    telefono         = Column(String(50))
    website          = Column(String(200))
    ciudad           = Column(String(100), index=True)
    empresa          = Column(String(200))
    lat              = Column(Float)
    lng              = Column(Float)
    fecha_extraccion = Column(DateTime, default=datetime.utcnow)

    posts = relationship("Post", back_populates="usuario", cascade="all, delete-orphan")
    todos = relationship("Todo", back_populates="usuario", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "posts"

    id               = Column(Integer, primary_key=True)
    user_id          = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    titulo           = Column(String(500), nullable=False)
    cuerpo           = Column(Text, nullable=False)
    longitud_titulo  = Column(Integer)
    longitud_cuerpo  = Column(Integer)
    num_palabras     = Column(Integer)
    fecha_extraccion = Column(DateTime, default=datetime.utcnow)

    usuario     = relationship("Usuario", back_populates="posts")
    comentarios = relationship("Comentario", back_populates="post", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_post_user", "user_id"),)


class Comentario(Base):
    __tablename__ = "comentarios"

    id               = Column(Integer, primary_key=True)
    post_id          = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    nombre           = Column(String(500), nullable=False)
    email            = Column(String(200), nullable=False)
    cuerpo           = Column(Text, nullable=False)
    longitud_body    = Column(Integer)
    num_palabras     = Column(Integer)
    dominio_email    = Column(String(100), index=True)
    fecha_extraccion = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="comentarios")


class Todo(Base):
    __tablename__ = "todos"

    id               = Column(Integer, primary_key=True)
    user_id          = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    titulo           = Column(String(500), nullable=False)
    completado       = Column(Boolean, default=False, index=True)
    fecha_extraccion = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="todos")


class MetricasETL(Base):
    __tablename__ = "metricas_etl"

    id                        = Column(Integer, primary_key=True, autoincrement=True)
    fecha_ejecucion           = Column(DateTime, default=datetime.utcnow, index=True)
    usuarios_cargados         = Column(Integer, default=0)
    posts_cargados            = Column(Integer, default=0)
    comentarios_cargados      = Column(Integer, default=0)
    todos_cargados            = Column(Integer, default=0)
    tiempo_ejecucion_segundos = Column(Float)
    estado                    = Column(String(20))
    mensaje                   = Column(Text)


def create_all():
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas en PostgreSQL")


if __name__ == "__main__":
    test_connection()
    create_all()