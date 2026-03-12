"""
GestorBase - Clase padre para todos los gestores de datos.
Proporciona métodos CRUD genéricos que todas las clases hija heredan.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class GestorBase:
    """Clase base para gestionar datos en JSON."""
    
    def __init__(self, archivo: str, datos_default: List[Dict] = None):
        """
        Inicializa el gestor.
        
        Args:
            archivo: Nombre del archivo JSON (ej: "almuerzos.json")
            datos_default: Lista por defecto si el archivo está vacío
        """
        self.datos_default = datos_default or []
        # Ir de bot/menu_logic/base.py -> bot/ -> proyecto/ -> data/
        self.DATA_DIR = Path(__file__).parent.parent.parent / "data"
        self.FILE = self.DATA_DIR / archivo
    
    def _load(self) -> List[Dict]:
        """Carga datos desde el archivo JSON."""
        if not self.FILE.exists() or self.FILE.stat().st_size == 0:
            return self.datos_default.copy()
        
        with open(self.FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                return self.datos_default.copy()
            return json.loads(content)
    
    def _save(self, datos: List[Dict]) -> None:
        """Guarda datos en el archivo JSON."""
        with open(self.FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
    
    def get_all(self) -> List[Dict]:
        """Retorna todos los registros."""
        return self._load()
    
    def get_by_id(self, id: int) -> Optional[Dict]:
        """Busca un registro por ID."""
        datos = self._load()
        for d in datos:
            if d.get("id") == id:
                return d
        return None
    
    def get_by_categoria(self, categoria: str) -> List[Dict]:
        """Retorna registros que tienen la categoría especificada."""
        datos = self._load()
        return [d for d in datos if d.get("categoria", "").upper() == categoria.upper()]
    
    def create(self, **kwargs) -> Dict:
        """Crea un nuevo registro. Genera ID automáticamente."""
        datos = self._load()
        nuevo_id = max([d.get("id", 0) for d in datos], default=0) + 1
        
        registro = {"id": nuevo_id}
        registro.update(kwargs)
        
        datos.append(registro)
        self._save(datos)
        return registro
    
    def update(self, id: int, **kwargs) -> Optional[Dict]:
        """Actualiza un registro por ID. Retorna el registro actualizado o None."""
        datos = self._load()
        
        for i, d in enumerate(datos):
            if d.get("id") == id:
                datos[i].update(kwargs)
                self._save(datos)
                return datos[i]
        
        return None
    
    def delete(self, id: int) -> bool:
        """Elimina un registro por ID y reindexa los IDs."""
        datos = self._load()
        inicial = len(datos)
        datos = [d for d in datos if d.get("id") != id]
        
        if len(datos) < inicial:
            # Reindexar IDs
            for i, d in enumerate(datos, 1):
                d["id"] = i
            self._save(datos)
            return True
        
        return False
    
    def get_all_categorias(self) -> List[str]:
        """Retorna lista de categorías únicas."""
        datos = self._load()
        cats = set()
        for d in datos:
            if d.get("categoria"):
                cats.add(d["categoria"])
        return sorted(list(cats))
