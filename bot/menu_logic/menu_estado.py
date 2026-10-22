"""
Gestor de Estado del Menú.
Controla la regla RN01: Solo un menú por día.
"""

from datetime import date
from .base import GestorBase


class GestorMenuEstado(GestorBase):
    """Gestor para controlar el estado del menú diario."""

    def __init__(self):
        # Estado inicial: sin menú generado
        super().__init__("menu_estado.json", [])

    def obtener_fecha_ultimo_menu(self) -> str:
        """Retorna la fecha del último menú generado (formato YYYY-MM-DD) o None."""
        datos = self._load()
        if datos and len(datos) > 0:
            return datos[0].get("fecha_ultimo_menu")
        return None

    def registrar_menu_generado(self) -> None:
        """Registra que se generó un menú hoy."""
        datos = [{
            "fecha_ultimo_menu": date.today().isoformat()
        }]
        self._save(datos)

    def puede_generar_menu(self) -> bool:
        """
        Verifica si se puede generar un menú hoy.
        Retorna True si no hay menú generado hoy, False si ya existe.
        """
        fecha_ultimo = self.obtener_fecha_ultimo_menu()
        if fecha_ultimo is None:
            return True

        return fecha_ultimo != date.today().isoformat()

    def obtener_mensaje_bloqueo(self) -> str:
        """Retorna un mensaje explicando por qué no se puede generar el menú."""
        return (
            "⚠️ Ya se ha generado un menú hoy.\n\n"
            "La regla de negocio (RN01) permite solo un menú por día.\n"
            "Podrás generar un nuevo menú mañana."
        )