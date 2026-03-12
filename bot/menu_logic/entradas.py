"""
Gestor de Entradas.
Las entradas son solo nombres (texto simple).
"""

from .base import GestorBase


class GestorEntradas(GestorBase):
    """Gestor específico para entradas."""
    
    def __init__(self):
        super().__init__("entradas.json")
    
    def create(self, nombre: str) -> dict:
        """Crea una entrada (solo necesita nombre)."""
        return super().create(nombre=nombre)
