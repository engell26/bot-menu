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
import re
from typing import Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from menu_logic.almuerzos import GestorAlmuerzos
from menu_logic.entradas import GestorEntradas
from menu_logic.categorias import GestorCategorias
from menu_logic.acompanamientos import GestorAcompanamientos
from menu_logic.menu_estado import GestorMenuEstado


# === FUNCIONES DE VALIDACIÓN Y SANITIZACIÓN ===

MAX_INPUT_LENGTH = 200  # Longitud máxima para nombres y descripciones
MAX_ID_VALUE = 10000     # Valor máximo permitido para IDs


def sanitizar_texto(texto: str) -> str:
    """
    Sanitiza texto de usuario para prevenir inyección de datos.
    - Limita longitud
    - Elimina caracteres de control peligrosos
    - Normaliza espacios en blanco
    """
    if not texto:
        return ""

    # Limitar longitud
    texto = texto[:MAX_INPUT_LENGTH]

    # Eliminar caracteres de control (excepto salto de línea permitido en descripciones)
    texto = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', texto)

    # Normalizar espacios múltiples a uno solo
    texto = re.sub(r'\s+', ' ', texto)

    # Eliminar espacios al inicio y final
    texto = texto.strip()

    return texto


def validar_callback_id(callback_data: str, prefijo: str) -> Optional[int]:
    """
    Extrae y valida un ID numérico de callback_data.
    Retorna el ID si es válido, None si es inválido.

    Ejemplo: validar_callback_id("del_almuerzos_5", "del_almuerzos_") -> 5
    """
    if not callback_data or not prefijo:
        return None

    try:
        id_str = callback_data.replace(prefijo, "")
        id_val = int(id_str)

        # Validar que el ID esté en rango razonable
        if id_val < 1 or id_val > MAX_ID_VALUE:
            return None

        return id_val
    except (ValueError, AttributeError):
        return None


def parsear_callback_tipo_id(callback_data: str, prefijo: str) -> Optional[Tuple[str, int]]:
    """
    Parsea callback_data con formato prefijo_tipo_id.
    Retorna (tipo, id) si es válido, None si es inválido.

    Ejemplo: parsear_callback_tipo_id("del_almuerzos_5", "del_") -> ("almuerzos", 5)
    """
    if not callback_data or not prefijo:
        return None

    try:
        partes = callback_data.split("_")
        if len(partes) < 3:
            return None

        tipo = partes[1]
        id_str = partes[2]
        id_val = int(id_str)

        # Validar tipo permitido
        tipos_validos = {"almuerzos", "entradas", "acompanamientos"}
        if tipo not in tipos_validos:
            return None

        # Validar ID en rango
        if id_val < 1 or id_val > MAX_ID_VALUE:
            return None

        return (tipo, id_val)
    except (ValueError, AttributeError):
        return None

almuerzos_db = GestorAlmuerzos()
entradas_db = GestorEntradas()
categorias_db = GestorCategorias()
acompanamientos_db = GestorAcompanamientos()
menu_estado_db = GestorMenuEstado()

load_dotenv()
TOKEN = os.getenv("TOKEN")
app = Application.builder().token(TOKEN).build()

ESTADO_NOMBRE, ESTADO_DESC, ESTADO_CAT = range(3)

ESTADO_GEN_ESPECIALES = 100
ESTADO_GEN_ENTRADAS = 101
ESTADO_GEN_ALMUERZOS = 102
ESTADO_GEN_ACOMPANAMIENTOS = 103
ESTADO_GEN_VISTA_PREVIA = 104


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
        [InlineKeyboardButton("🍚 Acompañamientos", callback_data="gest_acompanamientos")],
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


async def gest_acompanamientos(update, context):
    query = update.callback_query
    await query.answer()
    context.user_data["gest_tipo"] = "acompanamientos"
    await query.edit_message_text(
        "🍚 Gestión de Acompañamientos\n\nSelecciona una opción:",
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
        [InlineKeyboardButton("✏️ Editar Nombre", callback_data="cat_editar_nombre")],
        [InlineKeyboardButton("✏️ Editar Precio", callback_data="cat_editar_precio")],
        [InlineKeyboardButton("🔙 Volver", callback_data="menu_gestion")]
    ]
    
    await query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(keyboard))


async def cat_editar_nombre(update, context):
    query = update.callback_query
    await query.answer()
    
    categorias = categorias_db.get_all()
    keyboard = []
    for c in categorias:
        keyboard.append([InlineKeyboardButton(f"✏️ {c['nombre']}", callback_data=f"catn_{c['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="gest_categorias")])
    
    await query.edit_message_text("Selecciona la categoría para editar su nombre:", reply_markup=InlineKeyboardMarkup(keyboard))


async def cat_editar_precio(update, context):
    query = update.callback_query
    await query.answer()
    
    categorias = categorias_db.get_all()
    keyboard = []
    for c in categorias:
        keyboard.append([InlineKeyboardButton(f"✏️ {c['nombre']}", callback_data=f"catp_{c['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="gest_categorias")])
    
    await query.edit_message_text("Selecciona la categoría para editar su precio:", reply_markup=InlineKeyboardMarkup(keyboard))


async def cat_seleccionar_nombre(update, context):
    query = update.callback_query
    await query.answer()

    cat_id = validar_callback_id(query.data, "catn_")
    if cat_id is None:
        await query.edit_message_text("❌ ID de categoría inválido.", reply_markup=gestion_keyboard())
        return ConversationHandler.END

    context.user_data["cat_id"] = cat_id

    await query.edit_message_text("Ingresa el nuevo nombre de la categoría:")
    return 20


async def cat_seleccionar_precio(update, context):
    query = update.callback_query
    await query.answer()

    cat_id = validar_callback_id(query.data, "catp_")
    if cat_id is None:
        await query.edit_message_text("❌ ID de categoría inválido.", reply_markup=gestion_keyboard())
        return ConversationHandler.END

    context.user_data["cat_id"] = cat_id

    await query.edit_message_text("Ingresa el nuevo precio (solo números):")
    return 21


async def cat_guardar_nombre(update, context):
    cat_id = context.user_data.get("cat_id")
    nuevo_nombre = sanitizar_texto(update.message.text)

    if not nuevo_nombre:
        await update.message.reply_text("❌ El nombre no puede estar vacío.")
        return 20

    categorias_db.update(cat_id, nombre=nuevo_nombre)
    await update.message.reply_text("✅ Nombre actualizado.", reply_markup=gestion_keyboard())
    return ConversationHandler.END


async def cat_guardar_precio(update, context):
    cat_id = context.user_data.get("cat_id")
    try:
        nuevo_precio = int(update.message.text)
        if nuevo_precio < 0:
            await update.message.reply_text("❌ El precio no puede ser negativo.")
            return 21
        categorias_db.update(cat_id, precio=nuevo_precio)
        await update.message.reply_text("✅ Precio actualizado.", reply_markup=gestion_keyboard())
    except ValueError:
        await update.message.reply_text("❌ Error: escribí solo números")
    return ConversationHandler.END


# === CRUD GENÉRICO ===

async def opc_ver(update, context):
    query = update.callback_query
    await query.answer()
    
    tipo = context.user_data.get("gest_tipo", "almuerzos")
    
    if tipo == "almuerzos":
        datos = almuerzos_db.get_all()
    elif tipo == "entradas":
        datos = entradas_db.get_all()
    elif tipo == "acompanamientos":
        datos = acompanamientos_db.get_all()
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
    elif tipo == "entradas":
        texto = "📋 Entradas:\n\n"
        for d in datos:
            texto += f"{d['id']}. {d['nombre']}\n"
    else:  # acompanamientos
        texto = "📋 Acompañamientos:\n\n"
        for d in datos:
            texto += f"{d['id']}. {d['nombre']}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data=f"gest_{tipo}")]]
    await query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(keyboard))


async def opc_registrar_start(update, context):
    query = update.callback_query
    await query.answer()
    tipo = context.user_data.get("gest_tipo", "almuerzos")
    
    await query.edit_message_text(
        f"📝 Registrando {tipo}\n\nIngresa el nombre:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Cancelar", callback_data="cancelar_")]
        ])
    )
    return ESTADO_NOMBRE


async def opc_registrar_nombre(update, context):
    nombre_sanitizado = sanitizar_texto(update.message.text)

    if not nombre_sanitizado:
        await update.message.reply_text("❌ El nombre no puede estar vacío. Intenta de nuevo:")
        return ESTADO_NOMBRE

    # Verificar duplicados para todos los tipos
    tipo = context.user_data.get("gest_tipo")
    if tipo == "almuerzos":
        existentes = almuerzos_db.get_all()
    elif tipo == "entradas":
        existentes = entradas_db.get_all()
    elif tipo == "acompanamientos":
        existentes = acompanamientos_db.get_all()
    else:
        existentes = []

    for item in existentes:
        if item.get("nombre", "").lower() == nombre_sanitizado.lower():
            await update.message.reply_text(
                f"❌ Ya existe un registro con el nombre '{nombre_sanitizado}'.",
                reply_markup=opciones_crud_keyboard(f"gest_{tipo}")
            )
            return ConversationHandler.END

    context.user_data["reg_nombre"] = nombre_sanitizado
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

    # Validar formato del callback
    categoria = query.data.replace("cat_", "")
    # Sanitizar el nombre de categoría (debe coincidir con categorías existentes)
    categoria_sanitizada = sanitizar_texto(categoria)

    # Verificar que la categoría existe
    categorias_validas = categorias_db.get_all_nombres()
    if categoria_sanitizada not in categorias_validas:
        await query.edit_message_text("❌ Categoría inválida.")
        return ConversationHandler.END

    context.user_data["reg_categoria"] = categoria_sanitizada

    await query.edit_message_text(
        f"Categoría seleccionada: {categoria_sanitizada}\n\n"
        "Ingresa la descripción (opcional) o /skip para omitir:"
    )
    return ESTADO_DESC


async def opc_registrar_desc(update, context):
    if update.message.text != "/skip":
        descripcion_sanitizada = sanitizar_texto(update.message.text)
        context.user_data["reg_descripcion"] = descripcion_sanitizada
    else:
        context.user_data["reg_descripcion"] = ""
    return await guardar_registro(update, context)


async def guardar_registro(update, context):
    tipo = context.user_data.get("gest_tipo")
    nombre = context.user_data.get("reg_nombre")
    categoria = context.user_data.get("reg_categoria", "")
    descripcion = context.user_data.get("reg_descripcion", "")

    if tipo == "almuerzos":
        nuevo = almuerzos_db.create(nombre=nombre, descripcion=descripcion, categoria=categoria)
        msg = f"✅ Almuerzo '{nuevo['nombre']}' registrado (ID: {nuevo['id']})"
    elif tipo == "entradas":
        nuevo = entradas_db.create(nombre=nombre)
        msg = f"✅ Entrada '{nuevo['nombre']}' registrada (ID: {nuevo['id']})"
    elif tipo == "acompanamientos":
        nuevo = acompanamientos_db.create(nombre=nombre)
        msg = f"✅ Acompañamiento '{nuevo['nombre']}' registrado (ID: {nuevo['id']})"
    else:
        msg = "❌ Error: tipo no reconocido"

    context.user_data.clear()
    context.user_data["gest_tipo"] = tipo

    await update.message.reply_text(msg, reply_markup=opciones_crud_keyboard(f"gest_{tipo}"))
    return ConversationHandler.END


async def opc_eliminar_start(update, context):
    query = update.callback_query
    await query.answer()
    
    tipo = context.user_data.get("gest_tipo", "almuerzos")
    
    if tipo == "almuerzos":
        datos = almuerzos_db.get_all()
    elif tipo == "entradas":
        datos = entradas_db.get_all()
    elif tipo == "acompanamientos":
        datos = acompanamientos_db.get_all()
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

    resultado = parsear_callback_tipo_id(query.data, "del_")
    if resultado is None:
        await query.edit_message_text("❌ Datos inválidos.", reply_markup=gestion_keyboard())
        return

    tipo, reg_id = resultado

    if tipo == "almuerzos":
        almuerzos_db.delete(reg_id)
    elif tipo == "entradas":
        entradas_db.delete(reg_id)
    elif tipo == "acompanamientos":
        acompanamientos_db.delete(reg_id)

    await query.edit_message_text("✅ Eliminado.", reply_markup=opciones_crud_keyboard(f"gest_{tipo}"))


async def opc_actualizar_start(update, context):
    query = update.callback_query
    await query.answer()
    
    tipo = context.user_data.get("gest_tipo", "almuerzos")
    
    if tipo == "almuerzos":
        datos = almuerzos_db.get_all()
    elif tipo == "entradas":
        datos = entradas_db.get_all()
    elif tipo == "acompanamientos":
        datos = acompanamientos_db.get_all()
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

    resultado = parsear_callback_tipo_id(query.data, "edit_")
    if resultado is None:
        await query.edit_message_text("❌ Datos inválidos.", reply_markup=gestion_keyboard())
        return ConversationHandler.END

    tipo, reg_id = resultado

    context.user_data["update_tipo"] = tipo
    context.user_data["update_id"] = reg_id

    await query.edit_message_text("Ingresa el nuevo nombre (o /skip para mantener):")
    return 10


async def opc_actualizar_nombre(update, context):
    if update.message.text != "/skip":
        nombre_sanitizado = sanitizar_texto(update.message.text)
        if nombre_sanitizado:
            context.user_data["update_nombre"] = nombre_sanitizado

    tipo = context.user_data.get("update_tipo")

    if tipo == "almuerzos":
        await update.message.reply_text("Ingresa la nueva categoría (o /skip para mantener):")
        return 11
    else:
        return await guardar_actualizacion(update, context)


async def opc_actualizar_cat(update, context):
    if update.message.text != "/skip":
        categoria_sanitizada = sanitizar_texto(update.message.text)
        # Verificar que la categoría existe
        categorias_validas = categorias_db.get_all_nombres()
        if categoria_sanitizada not in categorias_validas:
            await update.message.reply_text("❌ Categoría inválida. Intenta de nuevo o /skip:")
            return 11
        context.user_data["update_categoria"] = categoria_sanitizada

    await update.message.reply_text("Ingresa la nueva descripción (o /skip para mantener):")
    return 12


async def opc_actualizar_desc(update, context):
    if update.message.text != "/skip":
        descripcion_sanitizada = sanitizar_texto(update.message.text)
        context.user_data["update_descripcion"] = descripcion_sanitizada

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
    elif tipo == "acompanamientos":
        acompanamientos_db.update(reg_id, nombre=nombre)
        msg = "✅ Acompañamiento actualizado."
    else:
        msg = "❌ Error."
    
    tipo_original = tipo
    context.user_data.clear()
    context.user_data["gest_tipo"] = tipo_original
    
    await update.message.reply_text(msg, reply_markup=opciones_crud_keyboard(f"gest_{tipo_original}"))
    return ConversationHandler.END


# === GENERAR MENÚ ===

def inicializar_menu():
    return {
        "especiales": [],
        "entradas": [],
        "almuerzos": {},
        "acompanamientos": []
    }


def generar_keyboard_si_no(callback_prefix, volver_callback="menu_generar"):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Sí", callback_data=f"{callback_prefix}_si")],
        [InlineKeyboardButton("❌ No", callback_data=f"{callback_prefix}_no")],
        [InlineKeyboardButton("🔙 Volver", callback_data=volver_callback)]
    ])


async def menu_generar_start(update, context):
    query = update.callback_query
    await query.answer()
    
    context.user_data.clear()
    context.user_data["menu"] = inicializar_menu()
    
    await query.edit_message_text(
        "📝 Generar Menú\n\n¿Habrá especiales hoy?",
        reply_markup=generar_keyboard_si_no("gen_esp"))
    return ESTADO_GEN_ESPECIALES



async def gen_esp_confirmar_si(update, context):
    query = update.callback_query
    await query.answer()
    
    almuerzos_especiales = almuerzos_db.get_especiales()
    
    if not almuerzos_especiales:
        await query.edit_message_text(
            "No hay almuerzos con categoría 'ESPECIAL'.\n\n"
            "¿Habrá especiales hoy?",
            reply_markup=generar_keyboard_si_no("gen_esp"))
        return ESTADO_GEN_ESPECIALES
    
    context.user_data["menu_especiales_disponibles"] = almuerzos_especiales
    
    texto = "--- PARTE 1: ESPECIALES ---\n\n"
    texto += "Escribe los IDs separados por coma.\n"
    texto += "Ejemplo: 1,3,5\n\n"
    texto += "Almuerzos especiales:\n\n"
    for a in almuerzos_especiales:
        texto += f"{a['id']}. {a['nombre']}\n"
        if a.get('descripcion'):
            texto += f"   └ {a['descripcion']}\n"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Volver", callback_data="gen_volver_esp")]
    ])
    
    await query.edit_message_text(texto, reply_markup=keyboard)
    return ESTADO_GEN_ESPECIALES


async def gen_esp_confirmar_no(update, context):
    query = update.callback_query
    await query.answer()
    
    context.user_data["menu"]["especiales"] = []
    return await parte_entradas(update, context)


async def gen_volver_esp(update, context):
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📝 Generar Menú\n\n¿Habrá especiales hoy?",
        reply_markup=generar_keyboard_si_no("gen_esp"))
    return ESTADO_GEN_ESPECIALES


async def gen_volver_entradas(update, context):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "--- PARTE 2: ENTRADAS ---\n\n"
        "Escribe los IDs separados por coma, o /skip para omitir.\n"
        "Ejemplo: 1,3\n\n"
        "Entradas disponibles:\n\n" +
        "\n".join(f"{e['id']}. {e['nombre']}" for e in context.user_data.get("menu_entradas_disponibles", [])),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Volver", callback_data="menu_generar")]]))
    return ESTADO_GEN_ENTRADAS


async def guardar_especiales(update, context):
    try:
        texto = update.message.text.strip()
        if not texto:
            await update.message.reply_text("❌ Ingresa IDs. Ejemplo: 1,2,3")
            return ESTADO_GEN_ESPECIALES
        
        ids = [int(x.strip()) for x in texto.split(",")]
        disponibles = context.user_data.get("menu_especiales_disponibles", [])
        
        seleccionados = [a for a in disponibles if a["id"] in ids]
        
        if not seleccionados:
            await update.message.reply_text("❌ No se encontraron especiales con esos IDs.")
            return ESTADO_GEN_ESPECIALES
        
        context.user_data["menu"]["especiales"] = seleccionados
        return await parte_entradas(update, context)
        
    except ValueError:
        await update.message.reply_text("❌ Error. Ejemplo válido: 1,2,3")
        return ESTADO_GEN_ESPECIALES


async def parte_entradas(update, context):
    entradas = entradas_db.get_all()
    
    if not entradas:
        context.user_data["menu"]["entradas"] = []
        return await parte_almuerzos(update, context)
    
    context.user_data["menu_entradas_disponibles"] = entradas
    
    texto = "--- PARTE 2: ENTRADAS ---\n\n"
    texto += "Escribe los IDs separados por coma, o /skip para omitir.\n"
    texto += "Ejemplo: 1,3\n\n"
    texto += "Entradas disponibles:\n\n"
    for e in entradas:
        texto += f"{e['id']}. {e['nombre']}\n"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Volver", callback_data="gen_volver_entradas")]
    ])
    
    await update.message.reply_text(texto, reply_markup=keyboard)
    return ESTADO_GEN_ENTRADAS


async def guardar_entradas(update, context):
    texto = update.message.text.strip()
    
    if texto.lower() == "/skip":
        context.user_data["menu"]["entradas"] = []
        return await parte_almuerzos(update, context)
    
    try:
        ids = [int(x.strip()) for x in texto.split(",")]
        disponibles = context.user_data.get("menu_entradas_disponibles", [])
        
        seleccionados = [e for e in disponibles if e["id"] in ids]
        
        context.user_data["menu"]["entradas"] = seleccionados
        return await parte_almuerzos(update, context)
        
    except ValueError:
        await update.message.reply_text("❌ Error. Ejemplo: 1,2 o /skip")
        return ESTADO_GEN_ENTRADAS


async def parte_almuerzos(update, context):
    categorias = categorias_db.get_all()
    almuerzos = almuerzos_db.get_all()
    
    menu = context.user_data["menu"]
    
    texto = "--- PARTE 3: ALMUERZOS ---\n\n"
    
    menu["almuerzos"] = {}
    context.user_data["menu_categorias"] = []
    context.user_data["menu_idx_categoria"] = 0
    
    for cat in categorias:
        cat_nombre = cat["nombre"].upper()
        if cat_nombre == "ESPECIAL":
            continue
        almuerzos_cat = [a for a in almuerzos if a.get("categoria", "").upper() == cat_nombre]
        
        if almuerzos_cat:
            context.user_data["menu_categorias"].append({
                "nombre": cat["nombre"],
                "precio": cat.get("precio", 0),
                "almuerzos": almuerzos_cat
            })
    
    if not context.user_data["menu_categorias"]:
        await update.message.reply_text("No hay almuerzos registrados.")
        return await parte_acompanamientos(update, context)
    
    return await mostrar_siguiente_categoria(update, context)


async def mostrar_siguiente_categoria(update, context):
    idx = context.user_data["menu_idx_categoria"]
    categorias = context.user_data["menu_categorias"]
    
    if idx >= len(categorias):
        return await parte_acompanamientos(update, context)
    
    cat = categorias[idx]
    
    texto = f"--- PARTE 3: ALMUERZOS ({cat['nombre']}) ---\n\n"
    precio = f"${cat['precio']:,}" if cat['precio'] > 0 else "Sin precio"
    texto += f"Precio: {precio}\n\n"
    texto += "Escribe los IDs separados por coma, o /skip para omitir.\n"
    texto += "Ejemplo: 1,3,5\n\n"
    texto += "Almuerzos disponibles:\n\n"
    for a in cat["almuerzos"]:
        texto += f"{a['id']}. {a['nombre']}"
        if a.get('descripcion'):
            texto += f" - {a['descripcion']}"
        texto += "\n"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭️ Omitir categoría", callback_data="gen_skip_cat")],
        [InlineKeyboardButton("🔙 Volver", callback_data="gen_volver_cat")]
    ])
    
    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.message.reply_text(texto, reply_markup=keyboard)
    else:
        await update.message.reply_text(texto, reply_markup=keyboard)
    
    return ESTADO_GEN_ALMUERZOS


async def gen_skip_categoria(update, context):
    """Maneja el callback del botón omitir categoría."""
    query = update.callback_query
    await query.answer()
    
    idx = context.user_data["menu_idx_categoria"]
    categorias = context.user_data["menu_categorias"]
    
    if idx < len(categorias):
        cat = categorias[idx]
        context.user_data["menu"]["almuerzos"][cat["nombre"]] = []
        context.user_data["menu_idx_categoria"] = idx + 1
    
    await query.edit_message_text("⏭️ Categoría omitida.")
    
    idx = context.user_data["menu_idx_categoria"]
    if idx >= len(categorias):
        return await parte_acompanamientos(update, context)
    
    cat = categorias[idx]
    
    texto = f"--- PARTE 3: ALMUERZOS ({cat['nombre']}) ---\n\n"
    precio = f"${cat['precio']:,}" if cat['precio'] > 0 else "Sin precio"
    texto += f"Precio: {precio}\n\n"
    texto += "Escribe los IDs separados por coma, o /skip para omitir.\n"
    texto += "Ejemplo: 1,3,5\n\n"
    texto += "Almuerzos disponibles:\n\n"
    for a in cat["almuerzos"]:
        texto += f"{a['id']}. {a['nombre']}"
        if a.get('descripcion'):
            texto += f" - {a['descripcion']}"
        texto += "\n"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭️ Omitir categoría", callback_data="gen_skip_cat")],
        [InlineKeyboardButton("🔙 Volver", callback_data="gen_volver_cat")]
    ])
    
    await query.message.reply_text(texto, reply_markup=keyboard)
    return ESTADO_GEN_ALMUERZOS


async def guardar_almuerzos_categoria(update, context):
    texto = update.message.text.strip()
    idx = context.user_data["menu_idx_categoria"]
    categorias = context.user_data["menu_categorias"]
    cat = categorias[idx]
    
    if texto.lower() == "/skip":
        context.user_data["menu"]["almuerzos"][cat["nombre"]] = []
    else:
        try:
            ids = [int(x.strip()) for x in texto.split(",")]
            seleccionados = [a for a in cat["almuerzos"] if a["id"] in ids]
            context.user_data["menu"]["almuerzos"][cat["nombre"]] = seleccionados
        except ValueError:
            await update.message.reply_text("❌ Error. Ejemplo: 1,2 o /skip")
            return ESTADO_GEN_ALMUERZOS
    
    context.user_data["menu_idx_categoria"] = idx + 1
    return await mostrar_siguiente_categoria(update, context)


async def gen_volver_categoria(update, context):
    query = update.callback_query
    await query.answer()

    idx = context.user_data["menu_idx_categoria"]
    if idx > 0:
        context.user_data["menu_idx_categoria"] = idx - 1

    idx = context.user_data["menu_idx_categoria"]
    categorias = context.user_data["menu_categorias"]

    if idx >= len(categorias):
        return await parte_acompanamientos(update, context)

    cat = categorias[idx]

    texto = f"--- PARTE 3: ALMUERZOS ({cat['nombre']}) ---\n\n"
    precio = f"${cat['precio']:,}" if cat['precio'] > 0 else "Sin precio"
    texto += f"Precio: {precio}\n\n"
    texto += "Escribe los IDs separados por coma, o /skip para omitir.\n"
    texto += "Ejemplo: 1,3,5\n\n"
    texto += "Almuerzos disponibles:\n\n"
    for a in cat["almuerzos"]:
        texto += f"{a['id']}. {a['nombre']}"
        if a.get('descripcion'):
            texto += f" - {a['descripcion']}"
        texto += "\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭️ Omitir categoría", callback_data="gen_skip_cat")],
        [InlineKeyboardButton("🔙 Volver", callback_data="gen_volver_cat")]
    ])

    await query.message.reply_text(texto, reply_markup=keyboard)
    return ESTADO_GEN_ALMUERZOS


async def parte_acompanamientos(update, context):
    acompanamientos = acompanamientos_db.get_all()

    if not acompanamientos:
        context.user_data["menu"]["acompanamientos"] = []
        return await mostrar_vista_previa(update, context)

    context.user_data["menu_acompanamientos_disponibles"] = acompanamientos

    texto = "--- PARTE 4: ACOMPAÑAMIENTOS ---\n\n"
    texto += "Escribe los IDs separados por coma, o /skip para omitir.\n"
    texto += "Ejemplo: 1,3\n\n"
    texto += "Acompañamientos disponibles:\n\n"
    for a in acompanamientos:
        texto += f"{a['id']}. {a['nombre']}\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Volver", callback_data="menu_generar")]
    ])

    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.message.reply_text(texto, reply_markup=keyboard)
    else:
        await update.message.reply_text(texto, reply_markup=keyboard)
    return ESTADO_GEN_ACOMPANAMIENTOS



async def guardar_acompanamientos(update, context):
    texto = update.message.text.strip()
    
    if texto.lower() == "/skip":
        context.user_data["menu"]["acompanamientos"] = []
    else:
        try:
            ids = [int(x.strip()) for x in texto.split(",")]
            disponibles = context.user_data.get("menu_acompanamientos_disponibles", [])
            seleccionados = [a for a in disponibles if a["id"] in ids]
            context.user_data["menu"]["acompanamientos"] = seleccionados
        except ValueError:
            await update.message.reply_text("❌ Error. Ejemplo: 1,2 o /skip")
            return ESTADO_GEN_ACOMPANAMIENTOS
    
    return await mostrar_vista_previa(update, context)


async def mostrar_vista_previa(update, context):
    menu = context.user_data["menu"]

    texto = "=" * 40 + "\n"
    texto += "📋 VISTA PREVIA DEL MENÚ\n"
    texto += "=" * 40 + "\n\n"

    if menu["especiales"]:
        texto += "🌟 ESPECIALES\n"
        texto += "-" * 20 + "\n"
        for e in menu["especiales"]:
            texto += f"• {e['nombre']}"
            if e.get('descripcion'):
                texto += f" - {e['descripcion']}"
            texto += "\n"
        texto += "\n"

    if menu["entradas"]:
        texto += "🥗 ENTRADAS\n"
        texto += "-" * 20 + "\n"
        for e in menu["entradas"]:
            texto += f"• {e['nombre']}\n"
        texto += "\n"

    if menu["almuerzos"]:
        texto += "🍽️ ALMUERZOS\n"
        texto += "-" * 20 + "\n"
        for cat_nombre, almuerzos in menu["almuerzos"].items():
            precio = ""
            cat_info = next((c for c in context.user_data.get("menu_categorias", []) if c["nombre"] == cat_nombre), None)
            if cat_info and cat_info["precio"] > 0:
                precio = f" (${cat_info['precio']:,})"
            texto += f"\n📌 {cat_nombre}{precio}\n"
            if almuerzos:
                for a in almuerzos:
                    texto += f"  • {a['nombre']}"
                    if a.get('descripcion'):
                        texto += f" - {a['descripcion']}"
                    texto += "\n"
            else:
                texto += "  (No hay almuerzos)\n"
        texto += "\n"

    if menu["acompanamientos"]:
        texto += "🍚 ACOMPAÑAMIENTOS\n"
        texto += "-" * 20 + "\n"
        for a in menu["acompanamientos"]:
            texto += f"• {a['nombre']}\n"

    texto += "\n" + "=" * 40 + "\n"
    texto += "✅ Menú generado exitosamente.\n"
    texto += "=" * 40 + "\n\n"
    texto += "¿Qué deseas hacer?"

    await update.message.reply_text(texto, reply_markup=main_menu_keyboard())

    context.user_data.clear()
    return ConversationHandler.END


async def cancelar_conversacion(update, context):
    """Cancela la conversación actual y vuelve al menú principal."""
    context.user_data.clear()
    if update.message:
        await update.message.reply_text("❌ Operación cancelada.", reply_markup=gestion_keyboard())
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("❌ Operación cancelada.", reply_markup=gestion_keyboard())
    return ConversationHandler.END


# === CONVERSATION HANDLERS ===

conv_registrar = ConversationHandler(
    entry_points=[CallbackQueryHandler(opc_registrar_start, pattern="opc_registrar")],
    states={
        ESTADO_NOMBRE: [MessageHandler(filters.TEXT, opc_registrar_nombre)],
        50: [CallbackQueryHandler(seleccionar_categoria, pattern="^cat_")],
        ESTADO_DESC: [MessageHandler(filters.TEXT, opc_registrar_desc)]
    },
    fallbacks=[
        CommandHandler("cancel", cancelar_conversacion),
        CallbackQueryHandler(cancelar_conversacion, pattern="^cancelar_$")
    ]
)

conv_actualizar = ConversationHandler(
    entry_points=[CallbackQueryHandler(opc_actualizar_seleccionar, pattern="^edit_")],
    states={
        10: [MessageHandler(filters.TEXT, opc_actualizar_nombre)],
        11: [MessageHandler(filters.TEXT, opc_actualizar_cat)],
        12: [MessageHandler(filters.TEXT, opc_actualizar_desc)]
    },
    fallbacks=[
        CommandHandler("cancel", cancelar_conversacion),
        CallbackQueryHandler(cancelar_conversacion, pattern="^cancelar_$")
    ]
)

conv_generar = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(menu_generar_start, pattern="menu_generar"),
        CallbackQueryHandler(gen_esp_confirmar_si, pattern="gen_esp_si"),
        CallbackQueryHandler(gen_esp_confirmar_no, pattern="gen_esp_no"),
    ],
    states={
        ESTADO_GEN_ESPECIALES: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, guardar_especiales),
            CallbackQueryHandler(gen_volver_esp, pattern="gen_volver_esp")
        ],
        ESTADO_GEN_ENTRADAS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, guardar_entradas),
            CallbackQueryHandler(gen_volver_entradas, pattern="gen_volver_entradas")
        ],
        ESTADO_GEN_ALMUERZOS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, guardar_almuerzos_categoria),
            CallbackQueryHandler(gen_volver_categoria, pattern="gen_volver_cat"),
            CallbackQueryHandler(gen_skip_categoria, pattern="gen_skip_cat")
        ],
        ESTADO_GEN_ACOMPANAMIENTOS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, guardar_acompanamientos)
        ]
    },
    fallbacks=[
        CommandHandler("cancel", cancelar_conversacion),
        CallbackQueryHandler(cancelar_conversacion, pattern="^cancelar_$")
    ]
)

conv_categorias = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(cat_seleccionar_nombre, pattern="^catn_"),
        CallbackQueryHandler(cat_seleccionar_precio, pattern="^catp_")
    ],
    states={
        20: [MessageHandler(filters.TEXT & ~filters.COMMAND, cat_guardar_nombre)],
        21: [MessageHandler(filters.TEXT & ~filters.COMMAND, cat_guardar_precio)]
    },
    fallbacks=[
        CommandHandler("cancel", cancelar_conversacion),
        CallbackQueryHandler(cancelar_conversacion, pattern="^cancelar_$")
    ]
)


# === REGISTRO DE HANDLERS ===

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("salida", lambda u, c: u.message.reply_text("👋 ¡Hasta luego!")))

# ConversationHandlers primero (tienen prioridad)
app.add_handler(conv_registrar)
app.add_handler(conv_actualizar)
app.add_handler(conv_generar)
app.add_handler(conv_categorias)

# CallbackQueryHandlers - gestión
app.add_handler(CallbackQueryHandler(menu_volver_principal, pattern="menu_volver"))
app.add_handler(CallbackQueryHandler(menu_gestion, pattern="menu_gestion"))
app.add_handler(CallbackQueryHandler(menu_generar_start, pattern="menu_generar"))

app.add_handler(CallbackQueryHandler(gest_almuerzos, pattern="gest_almuerzos"))
app.add_handler(CallbackQueryHandler(gest_entradas, pattern="gest_entradas"))
app.add_handler(CallbackQueryHandler(gest_acompanamientos, pattern="gest_acompanamientos"))
app.add_handler(CallbackQueryHandler(gest_categorias, pattern="gest_categorias"))
app.add_handler(CallbackQueryHandler(opc_ver, pattern="opc_ver"))
app.add_handler(CallbackQueryHandler(opc_actualizar_start, pattern="opc_actualizar"))
app.add_handler(CallbackQueryHandler(opc_eliminar_start, pattern="opc_eliminar"))
app.add_handler(CallbackQueryHandler(opc_eliminar_callback, pattern="^del_"))
app.add_handler(CallbackQueryHandler(cat_editar_nombre, pattern="cat_editar_nombre"))
app.add_handler(CallbackQueryHandler(cat_editar_precio, pattern="cat_editar_precio"))

app.run_polling()
