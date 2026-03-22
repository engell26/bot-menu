# Bot Menú Glotón D.C.

Bot de Telegram para gestionar almuerzos de un restaurante.

---

## Estructura del Proyecto

```
bot-menu/
├── .env                  # Token del bot y variables de entorno
├── .gitignore
├── README.md
├── requirements.txt
├── bot.log               # Logs del bot
├── bot/
│   ├── bot.py            # Lógica principal del bot
│   ├── menu_logic/
│   │   ├── base.py       # Clase base con métodos CRUD
│   │   ├── categorias.py # Gestor de categorías
│   │   ├── almuerzos.py  # Gestor de almuerzos
│   │   ├── entradas.py   # Gestor de entradas
│   │   └── acompanamientos.py # Gestor de acompañamientos
│   └── __pycache__/
└── data/                 # Archivos JSON persistentes
    ├── almuerzos.json
    ├── entradas.json
    ├── acompanamientos.json
    └── categorias.json
```

---

## Comandos

- `/start` - Inicia el bot y muestra el menú principal
- `/salida` - Termina la sesión

---

## Funcionalidades

### Menú Principal

1. **Gestión** - Administrar el catálogo de productos
2. **Generar Menú** - Crear el menú del día

### Gestión de Catálogo

| Opción | Descripción |
|--------|-------------|
| Almuerzos | CRUD completo (registrar, actualizar, eliminar, ver todos) |
| Entradas | CRUD completo |
| Acompañamientos | CRUD completo |
| Categorías | Editar nombre y precio de las categorías |

### Generar Menú (En desarrollo)

- [x] Parte 1: Especiales del día
- [ ] Parte 2: Entradas
- [ ] Parte 3: Almuerzos por categoría
- [ ] Parte 4: Acompañamientos
- [ ] Parte 5: Vista previa

---

## Reglas de Negocio

| ID   | Regla |
|------|-------|
| RN01 | Solo un menú por día |
| RN02 | No se permiten almuerzos duplicados en el catálogo |
| RN03 | Los IDs se reindexan al eliminar registros |

---

## Tecnologías

| Tecnología | Uso |
|------------|-----|
| Python 3 | Lenguaje principal |
| python-telegram-bot | Comunicación con API de Telegram |
| python-dotenv | Gestión de variables de entorno |
| JSON | Persistencia de datos |

---

## Instalación

1. Crear entorno virtual:
   ```bash
   python -m venv venv
   ```

2. Activar entorno virtual:
   ```bash
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instalar dependencias:
   ```bash   pip install -r requirements.txt
   ```

4. Configurar `.env`:
   ```
   TOKEN=tu_token_de_telegram
   ```

5. Ejecutar:
   ```bash
   cd bot
   python bot.py
   ```
