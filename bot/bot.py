"""
Bot Menú Glotón D.C.
=====================
Bot de Telegram para gestionar almuerzos de un restaurante.

Comandos:
    /start - Muestra el menú principal
    /salida - Termina la sesión
"""

# === IMPORTS ===
from telegram.ext import Application, CommandHandler, filters, MessageHandler, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import menu_logic.almuerzos as almuerzos_db

# === CONFIGURACIÓN ===
load_dotenv()
TOKEN = os.getenv("TOKEN")
app = Application.builder().token(TOKEN).build()

# Estados para Generar Menú
(   # 1. Especiales
    CONFIRMAR_ESPECIALES, ELEGIR_ESPECIALES,
    # 2. Entradas
    ELEGIR_ENTRADAS,
    # 3. Almuerzos por categoría
    CATEGORIA_PRECIO, ELEGIR_ALMUERZOS,
    # 4. Acompañamientos
    ELEGIR_ACOMPANAMIENTOS,
    # 5. Vista previa
    VISTA_PREVIA
) = range(7)

# Estados para Gestión
ESTADO_GESTION_ALMUERZO, G_ESTADO_NOMBRE, G_ESTADO_DESC, G_ESTADO_CAT = range(4)


# === KEYBOARDS ===

def main_menu_keyboard():
    """
    Menú principal con 2 opciones:
    - Gestión: CRUD de entradas, almuerzos, acompañamientos
    - Generar Menú: crear el menú del día
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗂️ Gestión", callback_data="menu_gestion")],
        [InlineKeyboardButton("📝 Generar Menú", callback_data="menu_generar")]
    ])


def gestion_keyboard():
    """
    Submenú de gestión del catálogo.
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍽️ Almuerzos", callback_data="gest_almuerzos")],
        [InlineKeyboardButton("🥗 Entradas", callback_data="gest_entradas")],
        [InlineKeyboardButton("🍚 Acompañamientos", callback_data="gest_acompanamientos")],
        [InlineKeyboardButton("🔙 Volver", callback_data="menu_volver")]
    ])


def gestion_almuerzos_keyboard():
    """
    Opciones para gestionar almuerzos.
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Registrar", callback_data="reg_almuerzo")],
        [InlineKeyboardButton("✏️ Actualizar", callback_data="gest_alt_actualizar")],
        [InlineKeyboardButton("🗑️ Eliminar", callback_data="gest_alt_eliminar")],
        [InlineKeyboardButton("📋 Ver todos", callback_data="gest_alt_ver")],
        [InlineKeyboardButton("🔙 Volver", callback_data="menu_gestion")]
    ])


# === HANDLERS PRINCIPALES ===

async def start(update, context):
    """Comando /start - Muestra menú principal."""
    await update.message.reply_text(
        "🍽️ Bot Menú Glotón D.C.\n\n"
        "¿Qué deseas hacer?",
        reply_markup=main_menu_keyboard()
    )


async def menu_volver_principal(update, context):
    """Vuelve al menú principal."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🍽️ Bot Menú Glotón D.C.\n\n"
        "¿Qué deseas hacer?",
        reply_markup=main_menu_keyboard()
    )


# === GESTIÓN ===

async def menu_gestion(update, context):
    """Muestra el submenú de gestión."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🗂️ Gestión del Catálogo\n\n"
        "¿Qué deseas gestionar?",
        reply_markup=gestion_keyboard()
    )


async def gestion_almuerzos(update, context):
    """Muestra opciones para gestionar almuerzos."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🍽️ Gestión de Almuerzos\n\n"
        "Selecciona una opción:",
        reply_markup=gestion_almuerzos_keyboard()
    )


# === VER ALMUERZOS (GESTIÓN) ===

async def gest_alt_ver(update, context):
    """Muestra todos los almuerzos desde el menú de gestión."""
    query = update.callback_query
    await query.answer()
    
    almuerzos = almuerzos_db.get_all()
    if not almuerzos:
        await query.edit_message_text("No hay almuerzos registrados.")
    else:
        texto = "📋 Almuerzos registrados:\n\n"
        for a in almuerzos:
            cat = f" ({a.get('categoria', '')})" if a.get('categoria') else ""
            desc = f"\n   └ {a['descripcion']}" if a.get('descripcion') else ""
            texto += f"{a['id']}. {a['nombre']}{cat}{desc}\n"
        await query.edit_message_text(texto, reply_markup=gestion_almuerzos_keyboard())


# === REGISTRAR ALMUERZO (DESDE GESTIÓN) ===

async def reg_almuerzo_start(update, context):
    """Inicia registro de almuerzo desde gestión."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Ingresa el nombre del almuerzo:")
    return G_ESTADO_NOMBRE


async def reg_almuerzo_desc(update, context):
    """Segundo paso: pide descripción."""
    context.user_data["nombre"] = update.message.text
    await update.message.reply_text("Ingresa la descripción (opcional) o /skip para omitir:")
    return G_ESTADO_DESC


async def reg_almuerzo_cat(update, context):
    """Tercer paso: pide categoría y guarda."""
    context.user_data["descripcion"] = "" if update.message.text == "/skip" else update.message.text
    await update.message.reply_text("Ingresa la categoría sugerida:")
    return G_ESTADO_CAT


async def reg_almuerzo_fin(update, context):
    """Guarda el almuerzo y vuelve al menú de gestión."""
    context.user_data["categoria"] = update.message.text
    nuevo = almuerzos_db.create(
        context.user_data["nombre"],
        context.user_data["descripcion"],
        context.user_data["categoria"]
    )
    await update.message.reply_text(
        f"✅ Almuerzo '{nuevo['nombre']}' registrado con ID {nuevo['id']}\n\n"
        "🍽️ Gestión de Almuerzos",
        reply_markup=gestion_almuerzos_keyboard()
    )
    return ConversationHandler.END


# === ELIMINAR ALMUERZO (DESDE GESTIÓN) ===

async def gest_alt_eliminar_start(update, context):
    """Muestra almuerzos para eliminar."""
    query = update.callback_query
    await query.answer()
    
    almuerzos = almuerzos_db.get_all()
    if not almuerzos:
        await query.edit_message_text("No hay almuerzos para eliminar.")
        return
    
    keyboard = []
    for a in almuerzos:
        keyboard.append([InlineKeyboardButton(f"❌ {a['id']}. {a['nombre']}", callback_data=f"gest_del_{a['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="gest_almuerzos")])
    
    await query.edit_message_text("Selecciona el almuerzo a eliminar:", reply_markup=InlineKeyboardMarkup(keyboard))


async def gest_alt_eliminar_callback(update, context):
    """Elimina el almuerzo seleccionado."""
    query = update.callback_query
    await query.answer()
    
    almuerzo_id = int(query.data.split("_")[-1])
    almuerzos_db.delete(almuerzo_id)
    await query.edit_message_text(
        "✅ Almuerzo eliminado.\n\n🍽️ Gestión de Almuerzos",
        reply_markup=gestion_almuerzos_keyboard()
    )


# === ACTUALIZAR ALMUERZO (DESDE GESTIÓN) ===

async def gest_alt_actualizar_start(update, context):
    """Muestra almuerzos para actualizar."""
    query = update.callback_query
    await query.answer()
    
    almuerzos = almuerzos_db.get_all()
    if not almuerzos:
        await query.edit_message_text("No hay almuerzos para actualizar.")
        return
    
    keyboard = []
    for a in almuerzos:
        keyboard.append([InlineKeyboardButton(f"✏️ {a['id']}. {a['nombre']}", callback_data=f"gest_edit_{a['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="gest_almuerzos")])
    
    await query.edit_message_text("Selecciona el almuerzo a actualizar:", reply_markup=InlineKeyboardMarkup(keyboard))


async def gest_alt_actualizar_nombre(update, context):
    """Pide nuevo nombre."""
    query = update.callback_query
    await query.answer()
    
    almuerzo_id = int(query.data.split("_")[-1])
    context.user_data["edit_id"] = almuerzo_id
    await query.edit_message_text("Ingresa el nuevo nombre (envía /skip para mantener):")
    return 10  # Estado temporal


async def gest_alt_actualizar_desc(update, context):
    """Pide nueva descripción."""
    if update.message.text != "/skip":
        context.user_data["edit_nombre"] = update.message.text
    await update.message.reply_text("Ingresa la nueva descripción (envía /skip para mantener):")
    return 11  # Estado temporal


async def gest_alt_actualizar_fin(update, context):
    """Guarda los cambios."""
    if update.message.text != "/skip":
        context.user_data["edit_descripcion"] = update.message.text
    
    resultado = almuerzos_db.update(
        context.user_data["edit_id"],
        context.user_data.get("edit_nombre"),
        context.user_data.get("edit_descripcion"),
        None
    )
    
    if resultado:
        await update.message.reply_text(
            f"✅ Almuerzo actualizado.\n\n🍽️ Gestión de Almuerzos",
            reply_markup=gestion_almuerzos_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Error al actualizar.\n\n🍽️ Gestión de Almuerzos",
            reply_markup=gestion_almuerzos_keyboard()
        )
    return ConversationHandler.END


# === ENTRADAS Y ACOMPAÑAMIENTOS (POR AHORA SIMPLE) ===

async def gest_entradas(update, context):
    """Placeholder para entradas."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🥗 Gestión de Entradas\n\n"
        "Próximamente: CRUD de entradas\n\n🔙 Volver",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Volver", callback_data="menu_gestion")]
        ])
    )


async def gest_acompanamientos(update, context):
    """Placeholder para acompañamiento."""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🍚 Gestión de Acompañamientos\n\n"
        "Próximamente: CRUD de acompañamiento\n\n🔙 Volver",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Volver", callback_data="menu_gestion")]
        ])
    )


# === GENERAR MENÚ ===

async def menu_generar_start(update, context):
    """Inicia el flujo de generar menú - pregunta si hay especiales."""
    query = update.callback_query
    await query.answer()
    
    context.user_data["menu"] = {
        "especiales": [],
        "entradas": [],
        "almuerzos": {},
        "acompanamientos": []
    }
    
    await query.edit_message_text(
        "📝 Generar Menú\n\n"
        "¿Habrá especiales hoy?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Sí", callback_data="gen_esp_confirmar_si")],
            [InlineKeyboardButton("❌ No", callback_data="gen_esp_confirmar_no")],
            [InlineKeyboardButton("🔙 Volver", callback_data="menu_volver")]
        ])
    )


async def gen_esp_confirmar_si(update, context):
    """Usuario dijo sí a especiales - inicia conversation para elegir."""
    query = update.callback_query
    await query.answer()
    
    # Solo mostrar almuerzos con categoría ESPECIAL
    almuerzos = almuerzos_db.get_by_categoria("ESPECIAL")
    
    if not almuerzos:
        await query.edit_message_text(
            "No hay almuerzos con categoría 'ESPECIAL'.\n\n"
            "📝 Tip: Registra almuerzos en Gestión → Almuerzos → "
            "Registrar y usa la categoría 'ESPECIAL'.\n\n"
            "📝 Menú principal:",
            reply_markup=main_menu_keyboard()
        )
        return
    
    # Mostrar lista y pedir IDs
    texto = "--- PARTE 1: ESPECIALES ---\n\n"
    texto += "Escribe los IDs de los almuerzos separados por coma.\n"
    texto += "Ejemplo: 1,3,5\n\n"
    texto += "Almuerzos especiales disponibles:\n\n"
    for a in almuerzos:
        texto += f"{a['id']}. {a['nombre']}\n"
        if a.get('descripcion'):
            texto += f"   └ {a['descripcion']}\n"
    
    await query.edit_message_text(texto)
    return ELEGIR_ESPECIALES


async def gen_esp_confirmar_no(update, context):
    """Usuario dijo no a especiales - pasar a entradas."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "--- PARTE 2: ENTRADAS ---\n\n"
        "Esta parte se implementará pronto.\n\n"
        "📝 Menú principal:",
        reply_markup=main_menu_keyboard()
    )


async def gen_elegir_especiales(update, context):
    """Guarda los especiales seleccionados por IDs."""
    try:
        ids = [int(x.strip()) for x in update.message.text.split(",")]
        almuerzos = almuerzos_db.get_all()
        seleccionados = [a for a in almuerzos if a["id"] in ids]
        context.user_data["menu"]["especiales"] = seleccionados
        
        await update.message.reply_text(
            f"✅ {len(seleccionados)} especiales seleccionados.\n\n"
            "--- PARTE 2: ENTRADAS ---\n\n"
            "Esta parte se implementará pronto.\n\n"
            "📝 Menú principal:",
            reply_markup=main_menu_keyboard()
        )
    except ValueError:
        await update.message.reply_text(
            "❌ Error. Escribe los IDs separados por coma.\n"
            "Ejemplo: 1,2,3"
        )
        return ELEGIR_ESPECIALES
    
    return ConversationHandler.END


# === CONVERSATION HANDLERS ===

# Registro de almuerzo desde gestión
conv_reg_almuerzo = ConversationHandler(
    entry_points=[CallbackQueryHandler(reg_almuerzo_start, pattern="^reg_almuerzo$")],
    states={
        G_ESTADO_NOMBRE: [MessageHandler(filters.TEXT, reg_almuerzo_desc)],
        G_ESTADO_DESC: [MessageHandler(filters.TEXT, reg_almuerzo_cat)],
        G_ESTADO_CAT: [MessageHandler(filters.TEXT, reg_almuerzo_fin)]
    },
    fallbacks=[]
)

# Actualizar almuerzo desde gestión
conv_actualizar = ConversationHandler(
    entry_points=[CallbackQueryHandler(gest_alt_actualizar_nombre, pattern="^gest_edit_")],
    states={
        10: [MessageHandler(filters.TEXT, gest_alt_actualizar_desc)],
        11: [MessageHandler(filters.TEXT, gest_alt_actualizar_fin)]
    },
    fallbacks=[]
)

# Generar Menú - Conversation para elegir especiales por IDs
conv_generar = ConversationHandler(
    entry_points=[CallbackQueryHandler(menu_generar_start, pattern="menu_generar")],
    states={
        CONFIRMAR_ESPECIALES: [CallbackQueryHandler(gen_esp_confirmar_si, pattern="gen_esp_confirmar_si"),
                              CallbackQueryHandler(gen_esp_confirmar_no, pattern="gen_esp_confirmar_no")],
        ELEGIR_ESPECIALES: [MessageHandler(filters.TEXT, gen_elegir_especiales)]
    },
    fallbacks=[]
)

# === REGISTRO DE HANDLERS ===

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("salida", lambda u, c: u.message.reply_text("👋 ¡Hasta luego!")))

# Menú principal
app.add_handler(CallbackQueryHandler(menu_volver_principal, pattern="menu_volver"))
app.add_handler(CallbackQueryHandler(menu_gestion, pattern="menu_gestion"))
app.add_handler(CallbackQueryHandler(menu_generar_start, pattern="menu_generar"))

# Gestión
app.add_handler(CallbackQueryHandler(gestion_almuerzos, pattern="gest_almuerzos"))
app.add_handler(CallbackQueryHandler(gest_alt_ver, pattern="gest_alt_ver"))
app.add_handler(CallbackQueryHandler(gest_alt_eliminar_start, pattern="gest_alt_eliminar"))
app.add_handler(CallbackQueryHandler(gest_alt_eliminar_callback, pattern="^gest_del_"))
app.add_handler(CallbackQueryHandler(gest_alt_actualizar_start, pattern="gest_alt_actualizar"))
app.add_handler(CallbackQueryHandler(gest_entradas, pattern="gest_entradas"))
app.add_handler(CallbackQueryHandler(gest_acompanamientos, pattern="gest_acompanamientos"))

# Generar Menú - Botones de confirmar especiales
app.add_handler(CallbackQueryHandler(gen_esp_confirmar_si, pattern="gen_esp_confirmar_si"))
app.add_handler(CallbackQueryHandler(gen_esp_confirmar_no, pattern="gen_esp_confirmar_no"))

# ConversationHandlers
app.add_handler(conv_reg_almuerzo)
app.add_handler(conv_actualizar)
app.add_handler(conv_generar)

# === INICIO ===
app.run_polling()
