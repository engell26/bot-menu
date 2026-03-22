"""
Gestor de Acompañamientos.
"""

from .base import GestorBase


class GestorAcompanamientos(GestorBase):
    """Gestor específico para acompañamientos."""
    
    def __init__(self):
        super().__init__("acompanamientos.json")
