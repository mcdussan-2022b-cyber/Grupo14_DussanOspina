#!/usr/bin/env python3
"""
Loader ETL - Carga datos a PostgreSQL
CORHUILA | Ingeniería de Sistemas | Minería de Datos 2026
"""

import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, ".")

from scripts.extractor import JSONPlaceholderExtractor
from scripts.models import (
    SessionLocal, create_all,
    Usuario, Post, Comentario, Todo, MetricasETL,
)

Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/etl.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class ETLLoader:

    def __init__(self):
        self.db = SessionLocal()
        self.stats = {}

    def cargar_usuarios(self, registros):
        count = 0
        for r in registros:
            try:
                obj = self.db.get(Usuario, r["id"])
                if obj is None:
                    obj = Usuario(
                        id=r["id"],
                        nombre=r["nombre"],
                        username=r["username"],
                        email=r["email"],
                        telefono=r.get("telefono"),
                        website=r.get("website"),
                        ciudad=r.get("ciudad"),
                        empresa=r.get("empresa"),
                        lat=r.get("lat"),
                        lng=r.get("lng"),
                    )
                    self.db.add(obj)
                count += 1
            except Exception as e:
                logger.warning(f"⚠️ Error usuario {r.get('id')}: {e}")
        self.db.commit()
        return count

    def cargar_posts(self, registros):
        count = 0
        for r in registros:
            try:
                obj = self.db.get(Post, r["id"])
                if obj is None:
                    obj = Post(
                        id=r["id"],
                        user_id=r["user_id"],
                        titulo=r["titulo"],
                        cuerpo=r["cuerpo"],
                        longitud_titulo=r.get("longitud_titulo"),
                        longitud_cuerpo=r.get("longitud_cuerpo"),
                        num_palabras=r.get("num_palabras"),
                    )
                    self.db.add(obj)
                count += 1
            except Exception as e:
                logger.warning(f"⚠️ Error post {r.get('id')}: {e}")
        self.db.commit()
        return count

    def cargar_comentarios(self, registros):
        count = 0
        for r in registros:
            try:
                obj = self.db.get(Comentario, r["id"])
                if obj is None:
                    obj = Comentario(
                        id=r["id"],
                        post_id=r["post_id"],
                        nombre=r["nombre"],
                        email=r["email"],
                        cuerpo=r["cuerpo"],
                        longitud_body=r.get("longitud_body"),
                        num_palabras=r.get("num_palabras"),
                        dominio_email=r.get("dominio_email"),
                    )
                    self.db.add(obj)
                count += 1
            except Exception as e:
                logger.warning(f"⚠️ Error comentario {r.get('id')}: {e}")
        self.db.commit()
        return count

    def cargar_todos(self, registros):
        count = 0
        for r in registros:
            try:
                obj = self.db.get(Todo, r["id"])
                if obj is None:
                    obj = Todo(
                        id=r["id"],
                        user_id=r["user_id"],
                        titulo=r["titulo"],
                        completado=r["completado"],
                    )
                    self.db.add(obj)
                count += 1
            except Exception as e:
                logger.warning(f"⚠️ Error todo {r.get('id')}: {e}")
        self.db.commit()
        return count

    def ejecutar(self):
        t0 = time.time()
        logger.info("🔄 Iniciando pipeline ETL completo")

        extractor = JSONPlaceholderExtractor()
        datos = extractor.ejecutar()

        try:
            u = self.cargar_usuarios(datos["usuarios"])
            p = self.cargar_posts(datos["posts"])
            c = self.cargar_comentarios(datos["comentarios"])
            t = self.cargar_todos(datos["todos"])

            self.stats = {"usuarios": u, "posts": p, "comentarios": c, "todos": t}
            estado = "SUCCESS"
            mensaje = f"u={u} p={p} c={c} t={t}"
            logger.info(f"✅ Carga exitosa: {mensaje}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error en carga: {e}")
            estado = "FAILED"
            mensaje = str(e)

        elapsed = time.time() - t0
        metrica = MetricasETL(
            usuarios_cargados=self.stats.get("usuarios", 0),
            posts_cargados=self.stats.get("posts", 0),
            comentarios_cargados=self.stats.get("comentarios", 0),
            todos_cargados=self.stats.get("todos", 0),
            tiempo_ejecucion_segundos=elapsed,
            estado=estado,
            mensaje=mensaje,
        )
        self.db.add(metrica)
        self.db.commit()
        self.db.close()

        print("\n📊 RESUMEN DE CARGA")
        print("=" * 40)
        for k, v in self.stats.items():
            print(f"  {k:15s}: {v:>4} registros")
        print(f"  tiempo       : {elapsed:.2f}s")
        print(f"  estado       : {estado}")
        print("=" * 40)
        return estado == "SUCCESS"


if __name__ == "__main__":
    create_all()
    loader = ETLLoader()
    ok = loader.ejecutar()
    sys.exit(0 if ok else 1)
