import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent.parent / "data"
ALMUERZOS_FILE = DATA_DIR / "almuerzos.json"

def load_almuerzos():
    if not ALMUERZOS_FILE.exists() or ALMUERZOS_FILE.stat().st_size == 0:
        return []
    with open(ALMUERZOS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        if not content.strip():
            return []
        return json.loads(content)

def save_almuerzos(almuerzos):
    with open(ALMUERZOS_FILE, "w", encoding="utf-8") as f:
        json.dump(almuerzos, f, indent=2, ensure_ascii=False)

def get_all():
    return load_almuerzos()

def get_by_categoria(categoria):
    """Retorna lista de almuerzos que tienen la categoría especificada."""
    almuerzos = load_almuerzos()
    return [a for a in almuerzos if a.get("categoria", "").upper() == categoria.upper()]

def get_by_id(almuerzo_id):
    almuerzos = load_almuerzos()
    for a in almuerzos:
        if a["id"] == almuerzo_id:
            return a
    return None

def create(nombre, descripcion="", categoria=""):
    almuerzos = load_almuerzos()
    new_id = max([a["id"] for a in almuerzos], default=0) + 1
    almuerzo = {
        "id": new_id,
        "nombre": nombre,
        "descripcion": descripcion,
        "categoria": categoria
    }
    almuerzos.append(almuerzo)
    save_almuerzos(almuerzos)
    return almuerzo

def update(almuerzo_id, nombre=None, descripcion=None, categoria=None):
    almuerzos = load_almuerzos()
    for a in almuerzos:
        if a["id"] == almuerzo_id:
            if nombre is not None:
                a["nombre"] = nombre
            if descripcion is not None:
                a["descripcion"] = descripcion
            if categoria is not None:
                a["categoria"] = categoria
            save_almuerzos(almuerzos)
            return a
    return None

def delete(almuerzo_id):
    almuerzos = load_almuerzos()
    initial_len = len(almuerzos)
    almuerzos = [a for a in almuerzos if a["id"] != almuerzo_id]
    if len(almuerzos) < initial_len:
        for i, a in enumerate(almuerzos, 1):
            a["id"] = i
        save_almuerzos(almuerzos)
        return True
    return False
