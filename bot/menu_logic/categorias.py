"""
Gestor de Categorías.
Guarda las categorías definidas por el usuario (ej: ESPECIAL, POLLO, CARNE, etc.)
"""

from .base import GestorBase


class GestorCategorias(GestorBase):
    """Gestor específico para categorías."""
    
    def __init__(self):
        # Categorías por defecto
        defaults = [
            {"id": 1, "nombre": "ESPECIAL", "precio": 0},
            {"id": 2, "nombre": "POLLO", "precio": 18000},
            {"id": 3, "nombre": "CARNE", "precio": 20000},
            {"id": 4, "nombre": "PESCADO", "precio": 22000},
            {"id": 5, "nombre": "OTRO", "precio": 15000},
        ]
        super().__init__("categorias.json", defaults)
    
    def get_all_nombres(self) -> list:
        """Retorna solo los nombres de las categorías."""
        cats = self.get_all()
        return [c.get("nombre", "") for c in cats if c.get("nombre")]
    
    def get_precio(self, nombre_categoria: str) -> int:
        """Retorna el precio de una categoría."""
        cats = self.get_all()
        for c in cats:
            if c.get("nombre", "").upper() == nombre_categoria.upper():
                return c.get("precio", 0)
        return 0
    
    def update_precio(self, id: int, precio: int) -> bool:
        """Actualiza el precio de una categoría."""
        return self.update(id, precio=precio) is not None

    def delete(self, id: int) -> bool:
        """Elimina una categoría SIN reindexar IDs para preservar integridad."""
        datos = self._load()
        inicial = len(datos)
        datos = [d for d in datos if d.get("id") != id]

        if len(datos) < inicial:
            self._save(datos)
            return True

        return False
