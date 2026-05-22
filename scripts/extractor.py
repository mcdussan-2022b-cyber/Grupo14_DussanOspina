#!/usr/bin/env python3
"""
Extractor ETL - JSONPlaceholder API
CORHUILA | Ingeniería de Sistemas | Minería de Datos 2026
"""

import requests
import json
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path

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

BASE_URL = "https://jsonplaceholder.typicode.com"

class JSONPlaceholderExtractor:

    def __init__(self):
        self.session = requests.Session()
        self.stats = {}

    def _get(self, endpoint):
        url = f"{BASE_URL}/{endpoint}"
        try:
            resp = self.session.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"✅ Extraídos {len(data)} registros de /{endpoint}")
            return data
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout en /{endpoint}")
            return []
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP Error en /{endpoint}: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Error inesperado en /{endpoint}: {e}")
            return []

    def extraer_usuarios(self):
        data = self._get("users")
        registros = []
        for u in data:
            try:
                registros.append({
                    "id":            u["id"],
                    "nombre":        u["name"],
                    "username":      u["username"],
                    "email":         u["email"],
                    "telefono":      u.get("phone"),
                    "website":       u.get("website"),
                    "ciudad":        u["address"]["city"],
                    "empresa":       u["company"]["name"],
                    "lat":           float(u["address"]["geo"]["lat"]),
                    "lng":           float(u["address"]["geo"]["lng"]),
                    "fecha_extraccion": datetime.utcnow().isoformat(),
                })
            except Exception as e:
                logger.warning(f"⚠️ Usuario malformado: {e}")
        self.stats["usuarios"] = len(registros)
        return registros

    def extraer_posts(self):
        data = self._get("posts")
        registros = []
        for p in data:
            try:
                body = p.get("body", "")
                registros.append({
                    "id":              p["id"],
                    "user_id":         p["userId"],
                    "titulo":          p["title"],
                    "cuerpo":          body,
                    "longitud_titulo": len(p["title"]),
                    "longitud_cuerpo": len(body),
                    "num_palabras":    len(body.split()),
                    "fecha_extraccion": datetime.utcnow().isoformat(),
                })
            except Exception as e:
                logger.warning(f"⚠️ Post malformado: {e}")
        self.stats["posts"] = len(registros)
        return registros

    def extraer_comentarios(self):
        data = self._get("comments")
        registros = []
        for c in data:
            try:
                body = c.get("body", "")
                registros.append({
                    "id":            c["id"],
                    "post_id":       c["postId"],
                    "nombre":        c["name"],
                    "email":         c["email"],
                    "cuerpo":        body,
                    "longitud_body": len(body),
                    "num_palabras":  len(body.split()),
                    "dominio_email": c["email"].split("@")[-1],
                    "fecha_extraccion": datetime.utcnow().isoformat(),
                })
            except Exception as e:
                logger.warning(f"⚠️ Comentario malformado: {e}")
        self.stats["comentarios"] = len(registros)
        return registros

    def extraer_todos(self):
        data = self._get("todos")
        registros = []
        for t in data:
            try:
                registros.append({
                    "id":          t["id"],
                    "user_id":     t["userId"],
                    "titulo":      t["title"],
                    "completado":  t["completed"],
                    "fecha_extraccion": datetime.utcnow().isoformat(),
                })
            except Exception as e:
                logger.warning(f"⚠️ Todo malformado: {e}")
        self.stats["todos"] = len(registros)
        return registros

    def ejecutar(self):
        logger.info("🚀 Iniciando extracción ETL - JSONPlaceholder")
        resultado = {
            "usuarios":    self.extraer_usuarios(),
            "posts":       self.extraer_posts(),
            "comentarios": self.extraer_comentarios(),
            "todos":       self.extraer_todos(),
        }
        Path("data").mkdir(exist_ok=True)
        for nombre, registros in resultado.items():
            df = pd.DataFrame(registros)
            df.to_csv(f"data/{nombre}.csv", index=False)
            with open(f"data/{nombre}.json", "w") as f:
                json.dump(registros, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Guardado data/{nombre}.csv y data/{nombre}.json")
        logger.info("✅ Extracción completada!")
        return resultado


if __name__ == "__main__":
    ext = JSONPlaceholderExtractor()
    datos = ext.ejecutar()

    print("\n📊 RESUMEN DE EXTRACCIÓN")
    print("=" * 40)
    for nombre, registros in datos.items():
        print(f"  {nombre:15s}: {len(registros):>4} registros")
    print("=" * 40)