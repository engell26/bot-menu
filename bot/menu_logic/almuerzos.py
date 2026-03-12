"""
Gestor de Almuerzos.
"""

from .base import GestorBase


class GestorAlmuerzos(GestorBase):
    """Gestor específico para almuerzos."""
    
    def __init__(self):
        super().__init__("almuerzos.json")
    
    def get_normales(self):
        """Retorna almuerzos que NO son especiales."""
        datos = self._load()
        return [d for d in datos if d.get("categoria", "").upper() != "ESPECIAL"]
    
    def get_especiales(self):
        """Retorna almuerzos con categoría ESPECIAL."""
        return self.get_by_categoria("ESPECIAL")
