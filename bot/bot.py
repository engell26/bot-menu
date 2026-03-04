from telegram.ext import Application, CommandHandler, filters, MessageHandler, ConversationHandler
from dotenv import load_dotenv
import os

#carga datos del .env
load_dotenv()

#asignacion del token del environment
TOKEN  = os.getenv("TOKEN")

#pre asignacion de estados
NOMBRE, APELLIDO = range(2)

#inicializamos el bot
app = Application.builder().token(TOKEN).build()

#funciones del bot
async def start(update, context):
    await update.message.reply_text("¿Cuál es tu nombre?")
    return NOMBRE

async def pedir_Apellido(update, context):
    # guardamos el nombre
    context.user_data["nombre"] = update.message.text
    await update.message.reply_text("¿Cuál es tu apellido?")
    return APELLIDO

async def finalizar(update, context):
    context.user_data["apellido"] = update.message.text
    await update.message.reply_text("¡Listo!")
    return ConversationHandler.END

if __name__ == "__main__":

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
                        states={
                            NOMBRE:[MessageHandler(filters.TEXT, pedir_Apellido)],
                            APELLIDO: [MessageHandler(filters.TEXT, finalizar)]
                        },
                        fallbacks=[CommandHandler("cancelar", ConversationHandler.END)]
    )

    app.add_handler(conv_handler)

    #se inicia el bot
    app.run_polling()