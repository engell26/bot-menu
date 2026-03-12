"""
Bot Menú Glotón D.C.
=====================
Bot de Telegram para gestionar almuerzos de un restaurante.
"""

# === IMPORTS ===
from telegram.ext import Application, CommandHandler, filters, MessageHandler, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from menu_logic.almuerzos import GestorAlmuerzos
from menu_logic.entradas import GestorEntradas
from menu_logic.categorias import GestorCategorias

almuerzos_db = GestorAlmuerzos()
entradas_db = GestorEntradas()
categorias_db = GestorCategorias()

load_dotenv()
TOKEN = os.getenv("TOKEN")
app = Application.builder().token(TOKEN).build()

ESTADO_NOMBRE, ESTADO_DESC, ESTADO_CAT = range(3)


# === KEYBOARDS ===

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🗂️ Gestión", callback_data="menu_gestion")],
        [InlineKeyboardButton("📝 Generar Menú", callback_data="menu_generar")]
    ])


def gestion_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍽️ Almuerzos", callback_data="gest_almuerzos")],
        [InlineKeyboardButton("🥗 Entradas", callback_data="gest_entradas")],
        [InlineKeyboardButton("🏷️ Categorías", callback_data="gest_categorias")],
        [InlineKeyboardButton("🔙 Volver", callback_data="menu_volver")]
    ])


def opciones_crud_keyboard(volver_callback):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Registrar", callback_data="opc_registrar")],
        [InlineKeyboardButton("✏️ Actualizar", callback_data="opc_actualizar")],
        [InlineKeyboardButton("🗑️ Eliminar", callback_data="opc_eliminar")],
        [InlineKeyboardButton("📋 Ver todos", callback_data="opc_ver")],
        [InlineKeyboardButton("🔙 Volver", callback_data=volver_callback)]
    ])


# === HANDLERS PRINCIPALES ===

async def start(update, context):
    await update.message.reply_text(
        "🍽️ Bot Menú Glotón D.C.\n\n¿Qué deseas hacer?",
        reply_markup=main_menu_keyboard()
    )


async def menu_volver_principal(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🍽️ Bot Menú Glotón D.C.\n\n¿Qué deseas hacer?",
        reply_markup=main_menu_keyboard()
    )


# === GESTIÓN ===

async def menu_gestion(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🗂️ Gestión del Catálogo\n\n¿Qué deseas gestionar?",
        reply_markup=gestion_keyboard()
    )


async def gest_almuerzos(update, context):
    query = update.callback_query
    await query.answer()
    context.user_data["gest_tipo"] = "almuerzos"
    await query.edit_message_text(
        "🍽️ Gestión de Almuerzos\n\nSelecciona una opción:",
        reply_markup=opciones_crud_keyboard("menu_gestion")
    )


async def gest_entradas(update, context):
    query = update.callback_query
    await query.answer()
    context.user_data["gest_tipo"] = "entradas"
    await query.edit_message_text(
        "🥗 Gestión de Entradas\n\nSelecciona una opción:",
        reply_markup=opciones_crud_keyboard("menu_gestion")
    )


async def gest_categorias(update, context):
    query = update.callback_query
    await query.answer()
    
    categorias = categorias_db.get_all()
    texto = "🏷️ Categorías y Precios\n\n"
    for c in categorias:
        precio = f"${c.get('precio', 0):,}" if c.get('precio', 0) > 0 else "Sin precio"
        texto += f"{c['id']}. {c['nombre']} - {precio}\n"
    
    keyboard = [
        [InlineKeyboardButton("✏️ Editar Precio", callback_data="cat_editar")],
        [InlineKeyboardButton("🔙 Volver", callback_data="menu_gestion")]
    ]
    
    await query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(keyboard))


# === CRUD GENÉRICO ===

async def opc_ver(update, context):
    query = update.callback_query
    await query.answer()
    
    tipo = context.user_data.get("gest_tipo", "almuerzos")
    
    if tipo == "almuerzos":
        datos = almuerzos_db.get_all()
    elif tipo == "entradas":
        datos = entradas_db.get_all()
    else:
        datos = []
    
    if not datos:
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data=f"gest_{tipo}")]]
        await query.edit_message_text("No hay registros.", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    if tipo == "almuerzos":
        texto = "📋 Almuerzos:\n\n"
        for d in datos:
            cat = f" ({d.get('categoria')})" if d.get('categoria') else ""
            desc = f"\n   └ {d.get('descripcion')}" if d.get('descripcion') else ""
            texto += f"{d['id']}. {d['nombre']}{cat}{desc}\n"
    else:
        texto = "📋 Entradas:\n\n"
        for d in datos:
            texto += f"{d['id']}. {d['nombre']}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data=f"gest_{tipo}")]]
    await query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(keyboard))


async def opc_registrar_start(update, context):
    query = update.callback_query
    await query.answer()
    tipo = context.user_data.get("gest_tipo", "almuerzos")
    
    await query.edit_message_text(
        f"🔧 DEBUG: Registrando {tipo}\n\nIngresa el nombre:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Cancelar", callback_data="menu_gestion")]
        ])
    )
    return ESTADO_NOMBRE


async def opc_registrar_nombre(update, context):
    context.user_data["reg_nombre"] = update.message.text
    tipo = context.user_data.get("gest_tipo")
    
    if tipo == "almuerzos":
        cats = categorias_db.get_all_nombres()
        keyboard = []
        for cat in cats:
            keyboard.append([InlineKeyboardButton(cat, callback_data=f"cat_{cat}")])
        
        await update.message.reply_text(
            "Selecciona la categoría:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return 50
    else:
        return await guardar_registro(update, context)


async def seleccionar_categoria(update, context):
    """Maneja la selección de categoría por botón."""
    query = update.callback_query
    await query.answer()
    
    categoria = query.data.replace("cat_", "")
    context.user_data["reg_categoria"] = categoria
    
    await query.edit_message_text(
        f"Categoría seleccionada: {categoria}\n\n"
        "Ingresa la descripción (opcional) o /skip para omitir:"
    )
    return ESTADO_DESC


async def opc_registrar_desc(update, context):
    context.user_data["reg_descripcion"] = "" if update.message.text == "/skip" else update.message.text
    return await guardar_registro(update, context)


async def guardar_registro(update, context):
    tipo = context.user_data.get("gest_tipo")
    nombre = context.user_data.get("reg_nombre")
    categoria = context.user_data.get("reg_categoria", "")
    descripcion = context.user_data.get("reg_descripcion", "")
    
    debug_info = f"🔧 DEBUG:\n tipo={tipo}\n nombre={nombre}\n categoria={categoria}\n descripcion={descripcion}\n"
    
    if tipo == "almuerzos":
        nuevo = almuerzos_db.create(nombre=nombre, descripcion=descripcion, categoria=categoria)
        msg = f"✅ Almuerzo '{nuevo['nombre']}' registrado (ID: {nuevo['id']})"
    elif tipo == "entradas":
        nuevo = entradas_db.create(nombre=nombre)
        msg = f"✅ Entrada '{nuevo['nombre']}' registrada (ID: {nuevo['id']})"
    else:
        msg = "❌ Error: tipo no reconocido"
    
    context.user_data.clear()
    context.user_data["gest_tipo"] = tipo
    
    await update.message.reply_text(debug_info + "\n" + msg, reply_markup=opciones_crud_keyboard(f"gest_{tipo}"))
    return ConversationHandler.END


async def opc_eliminar_start(update, context):
    query = update.callback_query
    await query.answer()
    
    tipo = context.user_data.get("gest_tipo", "almuerzos")
    
    if tipo == "almuerzos":
        datos = almuerzos_db.get_all()
    elif tipo == "entradas":
        datos = entradas_db.get_all()
    else:
        datos = []
    
    if not datos:
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data=f"gest_{tipo}")]]
        await query.edit_message_text("No hay registros para eliminar.", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    keyboard = []
    for d in datos:
        nombre = d.get("nombre", "")
        keyboard.append([InlineKeyboardButton(f"❌ {d['id']}. {nombre}", callback_data=f"del_{tipo}_{d['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data=f"gest_{tipo}")])
    
    await query.edit_message_text("Selecciona para eliminar:", reply_markup=InlineKeyboardMarkup(keyboard))


async def opc_eliminar_callback(update, context):
    query = update.callback_query
    await query.answer()
    
    partes = query.data.split("_")
    tipo = partes[1]
    reg_id = int(partes[2])
    
    if tipo == "almuerzos":
        almuerzos_db.delete(reg_id)
    elif tipo == "entradas":
        entradas_db.delete(reg_id)
    
    await query.edit_message_text("✅ Eliminado.", reply_markup=opciones_crud_keyboard(f"gest_{tipo}"))


async def opc_actualizar_start(update, context):
    query = update.callback_query
    await query.answer()
    
    tipo = context.user_data.get("gest_tipo", "almuerzos")
    
    if tipo == "almuerzos":
        datos = almuerzos_db.get_all()
    elif tipo == "entradas":
        datos = entradas_db.get_all()
    else:
        datos = []
    
    if not datos:
        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data=f"gest_{tipo}")]]
        await query.edit_message_text("No hay registros para actualizar.", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    keyboard = []
    for d in datos:
        nombre = d.get("nombre", "")
        keyboard.append([InlineKeyboardButton(f"✏️ {d['id']}. {nombre}", callback_data=f"edit_{tipo}_{d['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data=f"gest_{tipo}")])
    
    await query.edit_message_text("Selecciona para actualizar:", reply_markup=InlineKeyboardMarkup(keyboard))


async def opc_actualizar_seleccionar(update, context):
    query = update.callback_query
    await query.answer()
    
    partes = query.data.split("_")
    tipo = partes[1]
    reg_id = int(partes[2])
    
    context.user_data["update_tipo"] = tipo
    context.user_data["update_id"] = reg_id
    
    await query.edit_message_text("Ingresa el nuevo nombre (o /skip para mantener):")
    return 10


async def opc_actualizar_nombre(update, context):
    if update.message.text != "/skip":
        context.user_data["update_nombre"] = update.message.text
    
    tipo = context.user_data.get("update_tipo")
    
    if tipo == "almuerzos":
        await update.message.reply_text("Ingresa la nueva categoría (o /skip para mantener):")
        return 11
    else:
        return await guardar_actualizacion(update, context)


async def opc_actualizar_cat(update, context):
    if update.message.text != "/skip":
        context.user_data["update_categoria"] = update.message.text
    
    await update.message.reply_text("Ingresa la nueva descripción (o /skip para mantener):")
    return 12


async def opc_actualizar_desc(update, context):
    if update.message.text != "/skip":
        context.user_data["update_descripcion"] = update.message.text
    
    return await guardar_actualizacion(update, context)


async def guardar_actualizacion(update, context):
    tipo = context.user_data.get("update_tipo")
    reg_id = context.user_data.get("update_id")
    
    nombre = context.user_data.get("update_nombre")
    descripcion = context.user_data.get("update_descripcion")
    categoria = context.user_data.get("update_categoria")
    
    if tipo == "almuerzos":
        almuerzos_db.update(reg_id, nombre=nombre, descripcion=descripcion, categoria=categoria)
        msg = "✅ Almuerzo actualizado."
    elif tipo == "entradas":
        entradas_db.update(reg_id, nombre=nombre)
        msg = "✅ Entrada actualizada."
    else:
        msg = "❌ Error."
    
    tipo_original = tipo
    context.user_data.clear()
    context.user_data["gest_tipo"] = tipo_original
    
    await update.message.reply_text(msg, reply_markup=opciones_crud_keyboard(f"gest_{tipo_original}"))
    return ConversationHandler.END


# === GENERAR MENÚ ===

async def menu_generar_start(update, context):
    query = update.callback_query
    await query.answer()
    
    context.user_data["menu"] = {
        "especiales": [],
        "entradas": [],
        "almuerzos": {},
        "acompanamientos": []
    }
    
    await query.edit_message_text(
        "📝 Generar Menú\n\n¿Habrá especiales hoy?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Sí", callback_data="gen_esp_confirmar_si")],
            [InlineKeyboardButton("❌ No", callback_data="gen_esp_confirmar_no")],
            [InlineKeyboardButton("🔙 Volver", callback_data="menu_volver")]
        ])
    )


async def gen_esp_confirmar_si(update, context):
    query = update.callback_query
    await query.answer()
    
    almuerzos = almuerzos_db.get_especiales()
    
    if not almuerzos:
        await query.edit_message_text(
            "No hay almuerzos con categoría 'ESPECIAL'.\n\n"
            "Tip: Registra almuerzos en Gestión → Almuerzos → Registrar.\n\n"
            "📝 Menú principal:",
            reply_markup=main_menu_keyboard()
        )
        return
    
    texto = "--- PARTE 1: ESPECIALES ---\n\n"
    texto += "Escribe los IDs separados por coma.\n"
    texto += "Ejemplo: 1,3,5\n\n"
    texto += "Almuerzos especiales:\n\n"
    for a in almuerzos:
        texto += f"{a['id']}. {a['nombre']}\n"
        if a.get('descripcion'):
            texto += f"   └ {a['descripcion']}\n"
    
    await query.edit_message_text(texto)
    return 100


async def gen_esp_confirmar_no(update, context):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "--- PARTE 2: ENTRADAS ---\n\n"
        "Esta parte se implementará pronto.\n\n"
        "📝 Menú principal:",
        reply_markup=main_menu_keyboard()
    )


async def gen_elegir_especiales(update, context):
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
        await update.message.reply_text("❌ Error. Ejemplo: 1,2,3")
        return 100
    
    return ConversationHandler.END


# === CONVERSATION HANDLERS ===

conv_registrar = ConversationHandler(
    entry_points=[CallbackQueryHandler(opc_registrar_start, pattern="opc_registrar")],
    states={
        ESTADO_NOMBRE: [MessageHandler(filters.TEXT, opc_registrar_nombre)],
        50: [CallbackQueryHandler(seleccionar_categoria, pattern="^cat_")],
        ESTADO_DESC: [MessageHandler(filters.TEXT, opc_registrar_desc)]
    },
    fallbacks=[]
)

conv_actualizar = ConversationHandler(
    entry_points=[CallbackQueryHandler(opc_actualizar_seleccionar, pattern="^edit_")],
    states={
        10: [MessageHandler(filters.TEXT, opc_actualizar_nombre)],
        11: [MessageHandler(filters.TEXT, opc_actualizar_cat)],
        12: [MessageHandler(filters.TEXT, opc_actualizar_desc)]
    },
    fallbacks=[]
)

conv_generar = ConversationHandler(
    entry_points=[CallbackQueryHandler(menu_generar_start, pattern="menu_generar")],
    states={
        100: [MessageHandler(filters.TEXT, gen_elegir_especiales)]
    },
    fallbacks=[]
)


# === REGISTRO DE HANDLERS ===

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("salida", lambda u, c: u.message.reply_text("👋 ¡Hasta luego!")))

app.add_handler(CallbackQueryHandler(menu_volver_principal, pattern="menu_volver"))
app.add_handler(CallbackQueryHandler(menu_gestion, pattern="menu_gestion"))
app.add_handler(CallbackQueryHandler(menu_generar_start, pattern="menu_generar"))

app.add_handler(CallbackQueryHandler(gest_almuerzos, pattern="gest_almuerzos"))
app.add_handler(CallbackQueryHandler(gest_entradas, pattern="gest_entradas"))
app.add_handler(CallbackQueryHandler(gest_categorias, pattern="gest_categorias"))

app.add_handler(CallbackQueryHandler(opc_ver, pattern="opc_ver"))
app.add_handler(CallbackQueryHandler(opc_eliminar_start, pattern="opc_eliminar"))
app.add_handler(CallbackQueryHandler(opc_eliminar_callback, pattern="^del_"))
app.add_handler(CallbackQueryHandler(opc_actualizar_start, pattern="opc_actualizar"))

app.add_handler(conv_registrar)
app.add_handler(conv_actualizar)
app.add_handler(conv_generar)

app.run_polling()
