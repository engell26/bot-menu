# Documento de Requerimientos - Bot Telegram Gloton D.C.

## 1. Descripcion General

Bot de Telegram para la gestion y generacion automatica del menu diario del restaurante Gloton D.C., entregado en formato Word (.docx) listo para editar y compartir.

---

## 2. Actores

| Actor | Descripcion |
|-------|-------------|
| Administrador | Dueno del restaurante y/o sus hijos. Usuarios de confianza con acceso total al bot. |

Nota: El acceso estara restringido por una lista de IDs de Telegram autorizados, configurada en el archivo .env.

---

## 3. Funcionalidades

### 3.1 Gestion de Almuerzos

| ID | Funcionalidad | Descripcion |
|----|--------------|-------------|
| F01 | Registrar almuerzo | Agregar un almuerzo al catalogo con nombre y precio |
| F02 | Ver almuerzos | Listar todos los almuerzos registrados |
| F03 | Eliminar almuerzo | Remover un almuerzo del catalogo |

Reglas:
- No se permiten nombres de almuerzos duplicados.
- Maximo estimado: 30 almuerzos en catalogo.
- Los datos se persisten en almuerzos.json.

---

### 3.2 Generacion del Menu del Dia

| ID | Paso | Descripcion |
|----|------|-------------|
| F04 | Seleccionar almuerzos | El usuario elige del catalogo que almuerzos van hoy |
| F05 | Confirmar precios | Verificar o actualizar el precio de cada almuerzo seleccionado |
| F06 | Agregar especiales | Ingresar los especiales del dia (nombre, descripcion, precio) |
| F07 | Revisar resumen | Ver un resumen completo antes de generar el documento |
| F08 | Generar Word | Producir el archivo .docx del menu y enviarlo por Telegram |

---

### 3.3 Especiales Automaticos por Dia

| Especial | Dias |
|----------|------|
| Parrillada Gloton | Sabado y Domingo |
| Bandeja Paisa | Solo Sabado |
| Frijolada | Solo Sabado |

El usuario puede confirmar o descartar cada especial sugerido antes de continuar.

---

### 3.4 Historial de Menus

- Se guardan algunos menus segun criterio del administrador.
- El archivo .docx se envia por Telegram para edicion manual si es necesario.

---

## 4. Reglas de Negocio

| ID | Regla |
|----|-------|
| RN01 | Solo un menu por dia. |
| RN02 | No se permiten almuerzos duplicados en el catalogo. |
| RN03 | Los especiales de fin de semana se sugieren automaticamente segun el dia. |
| RN04 | El usuario puede corregir cualquier dato en el paso de revision antes de generar el Word. |
| RN05 | Solo usuarios con ID de Telegram autorizado pueden usar el bot. |
| RN06 | El documento final se entrega en .docx para permitir ediciones manuales. |

---

## 5. Estructura del Proyecto

bot-menu/
  bot/
    bot.py              # Logica del bot, comandos y flujo conversacional
  menu/
    menu.py             # Generacion del documento Word
    almuerzos.py        # Gestion del catalogo de almuerzos (JSON)
  data/
    almuerzos.json      # Catalogo persistente de almuerzos
  templates/            # Plantilla base del menu
  output/               # Menus generados (no se sube a GitHub)
  .env                  # Token y IDs autorizados (no se sube a GitHub)
  .gitignore
  requirements.txt
  README.md

---

## 6. Tecnologias

| Tecnologia | Uso |
|------------|-----|
| Python 3 | Lenguaje principal |
| python-telegram-bot | Comunicacion con la API de Telegram |
| python-docx | Generacion del documento Word |
| python-dotenv | Gestion de variables de entorno |
| JSON | Persistencia del catalogo de almuerzos |

---

## 7. Flujo Principal - Generacion del Menu

/menu
  -> Mostrar catalogo -> Usuario selecciona almuerzos del dia
  -> Confirmar/actualizar precios de cada almuerzo seleccionado
  -> (Si es fin de semana) Sugerir especiales recurrentes -> Usuario confirma/descarta
  -> Hay mas especiales hoy? -> Usuario ingresa: nombre, descripcion, precio
  -> Mostrar resumen completo -> Usuario revisa y corrige si es necesario
  -> Generar .docx y enviar por Telegram

---

## 8. Contenido Fijo del Menu

- Logo del restaurante
- Entradas: Sancocho de pescado / Spaguetti en salsa napolitana / Arroz con leche
- Acompanamientos: Arroz, pimenton, maduro y ensalada
- Nota desechable: Por el desechable, para llevar o domicilio tiene un costo adicional de 1.500
- Pagos: Nequi - Daviplata 3144235079
- Direccion: Calle 70A # 86A-18
- Pedidos WhatsApp: 311 275 67 75
