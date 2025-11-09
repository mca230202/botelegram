import poplib
from email import parser
import time
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler
import asyncio
import re
import sys
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
POP3_SERVER = "pop3.kuku.lu"
EMAIL_ACCOUNTS = [
    ("nethomas018a@honeys.be","WDRg#M3ZfCJAxG"),
    ("nethomas15a5@honeys.be","53NOJWfYxGr8HK&j"),
    ("cuentaThomas05@usako.net","XLi)imufOQ6L"),
    ("cuentaThomas07@usako.net","a:gYkDObkmXTi1h"),
    ("cuentaThomas16@usako.net","R]CH(fSy+ox63)NQ"),
    ("cuentaThomas28@usako.net","4JDWab1X)nbydL"),
    ("cuentaThomas41@usako.net","UP]oXA1KHcunu"),
    ("cuentaThomas20@usako.net","94K[IJU_AICS2qhn"),
    ("nethomas2a81@honeys.be","iV$hf6idvX[d"),
    ("nethomas862u@honeys.be","JGSe-O9oK7mZPpb"),
    ("nethomas2184@honeys.be","7J#joyrMTzLQ{V("),
    ("nethomas916q@honeys.be","jJOwvt6in-dqf"),
    ("nethomas7f56@honeys.be","AGRG#H4Jm8aFB"),
    ("nethomas109y@honeys.be","HY]nvy(*TK2a! R0xO"),
    ("nethomas961f@honeys.be","dNd{RSZyrAWZ9G"),
    ("nethomas961w@honeys.be","]BnJ6oK[P:Xl"),
    ("nethomas19f6@honeys.be","yWjcU24ktu_VQS+q"),
    ("nethomas1a8y@honeys.be","GWG7fRXPw8ZmB+"),
    ("nethomas97g6@honeys.be","EFYZJSlgW+G5c:}P"),
    ("nethomas962s@honeys.be","1$BYWH0hW-El7io"),
    ("nethomas716a@honeys.be","sF}tOdJnTu#D8sg]"),
    ("nethomas14a5@honeys.be","t63FDOPhLoUml5&"),
    ("nethomas971d@honeys.be","H&KUOtsLvYa3"),
    ("nethomas9j71@honeys.be","OG1RPbvbUc:I"),
]
PORT = 995

# --- CONFIGURACIÓN DE TELEGRAM ---
TELEGRAM_TOKEN = "8305795277:AAEHB6FINb8GjXlWgk2I6T6AJpK0VZqvIBA"

TELEGRAM_CHAT_IDS = [
    5910916435, 1791117148, 5695562269, 1021277549,
    5836513962, 5850828120, 6767314967, 1137438609, 7360240142,
    5470876128, 1451249740, 1111737214, 7673978510, 5850909591,
    1581029678, 6160541808, 1227729423, 5987153884, 7651831770, 8370693961,
    1579793937, 6693922368, 7771540264, 8367272724, 6661729470, 6760211269,
    5593201016, 1392235267, 8364691286, 8276764044, 8410501491, 5695604052,
    880945915, 8281293369, 1540389579, 8137172507, 8417576668, 7336498086, 6992959662, 8272401238
]

# 🔹 Crear el bot de Telegram
bot = Bot(token=TELEGRAM_TOKEN)

# 📁 Archivo para guardar estado
STATE_FILE = "correos_procesados.json"

# 📝 Cargar/guardar estado persistente
def cargar_estado():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_estado(estado):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(estado, f)
    except Exception as e:
        print(f"⚠️ Error guardando estado: {e}")

# 🤖 Comando /start
async def start_command(update: Update, context):
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "Usuario"
    nombre = update.effective_user.first_name or "Usuario"
    
    esta_registrado = chat_id in TELEGRAM_CHAT_IDS
    
    if esta_registrado:
        mensaje = (
            f"✅ ¡Hola {nombre}!\n\n"
            f"🤖 Bot activo y funcionando correctamente\n"
            f"📬 Tu Chat ID: {chat_id}\n"
            f"📧 Estás registrado para recibir notificaciones de correos\n\n"
            f"⏳ Recibirás alertas automáticamente cuando lleguen correos importantes."
        )
    else:
        mensaje = (
            f"👋 ¡Hola {nombre}!\n\n"
            f"⚠️ Tu Chat ID ({chat_id}) NO está registrado\n\n"
            f"Para recibir notificaciones, contacta al administrador "
            f"y proporciona este ID."
        )
    
    await update.message.reply_text(mensaje)
    print(f"✅ /start recibido de {nombre} (@{username}) - ID: {chat_id}")

# 🔄 Revisión de correos
async def revisar_correos():
    # Cargar estado previo
    correos_procesados = cargar_estado()
    
    while True:
        for EMAIL_ACCOUNT, PASSWORD in EMAIL_ACCOUNTS:
            mail = None
            try:
                print(f"\n🔍 [{datetime.now().strftime('%H:%M:%S')}] Revisando {EMAIL_ACCOUNT}...")
                mail = poplib.POP3_SSL(POP3_SERVER, PORT, timeout=30)

                mail.user(EMAIL_ACCOUNT)
                mail.pass_(PASSWORD)

                num_messages = len(mail.list()[1])

                if num_messages == 0:
                    print(f"✅ Sin correos")
                    mail.quit()
                    await asyncio.sleep(3)
                    continue

                print(f"📩 {num_messages} correo(s) en servidor")

                # Inicializar cuenta en estado si no existe
                if EMAIL_ACCOUNT not in correos_procesados:
                    correos_procesados[EMAIL_ACCOUNT] = []

                correos_enviados = 0

                for i in range(1, num_messages + 1):
                    try:
                        # Obtener el correo
                        raw_email = b"\n".join(mail.retr(i)[1])
                        email_message = parser.Parser().parsestr(raw_email.decode(errors='replace'))

                        # Crear hash único basado en múltiples campos
                        asunto = email_message.get('subject', '')
                        fecha = email_message.get('date', '')
                        message_id = email_message.get('Message-ID', '')
                        
                        # Hash único combinando varios campos
                        hash_correo = f"{asunto}|{fecha}|{message_id}"[:200]
                        
                        # Verificar si ya fue procesado
                        if hash_correo in correos_procesados[EMAIL_ACCOUNT]:
                            print(f"⏭️  Correo {i} ya procesado anteriormente")
                            mail.dele(i)
                            continue

                        # Extraer contenido
                        content = ""
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() in ["text/plain", "text/html"]:
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        content += payload.decode(errors='replace')
                        else:
                            payload = email_message.get_payload(decode=True)
                            if payload:
                                content = payload.decode(errors='replace')

                        # Buscar URLs
                        boton_match = re.search(r'enviada desde.*?(https?://[^\s"\'<>]+)', content, re.IGNORECASE | re.DOTALL)
                        boton_match2 = re.search(r'<a[^>]+href=["\'](https?://[^\s"\'<>]+)["\'][^>]*>\s*Obtener código\s*</a>', content, re.IGNORECASE)

                        url_encontrado = None
                        if boton_match:
                            url_encontrado = boton_match.group(1)
                        elif boton_match2:
                            url_encontrado = boton_match2.group(1)

                        if url_encontrado:
                            # Limpiar URL
                            url_encontrado = url_encontrado.split('&amp;')[0]
                            url_encontrado = url_encontrado.strip()
                            
                            # Verificar que la URL no esté vacía o sea inválida
                            if len(url_encontrado) > 10 and url_encontrado.startswith('http'):
                                mensaje = (
                                    f"📬 Nuevo correo en {EMAIL_ACCOUNT}!\n"
                                    f"🔗 {url_encontrado}"
                                )
                                
                                # Enviar a todos
                                enviados_exitosos = 0
                                for chat_id in TELEGRAM_CHAT_IDS:
                                    try:
                                        await bot.send_message(chat_id=chat_id, text=mensaje)
                                        enviados_exitosos += 1
                                        await asyncio.sleep(0.03)
                                    except Exception as e:
                                        pass  # Ignorar errores individuales
                                
                                print(f"✅ Correo {i} enviado a {enviados_exitosos} usuarios")
                                correos_enviados += 1
                                
                                # Marcar como procesado
                                correos_procesados[EMAIL_ACCOUNT].append(hash_correo)
                                
                                # Mantener solo los últimos 50 hashes por cuenta
                                if len(correos_procesados[EMAIL_ACCOUNT]) > 50:
                                    correos_procesados[EMAIL_ACCOUNT] = correos_procesados[EMAIL_ACCOUNT][-50:]
                                
                                # Guardar estado inmediatamente
                                guardar_estado(correos_procesados)

                        # SIEMPRE eliminar el correo después de procesarlo
                        mail.dele(i)

                    except Exception as e:
                        print(f"❌ Error en correo {i}: {str(e)[:100]}")
                        try:
                            mail.dele(i)  # Eliminar incluso si hay error
                        except:
                            pass

                # Cerrar conexión
                mail.quit()
                
                if correos_enviados > 0:
                    print(f"✨ {correos_enviados} correo(s) nuevo(s) procesado(s)")

            except poplib.error_proto as e:
                print(f"⛔ Error POP3: {str(e)[:100]}")

            except Exception as e:
                print(f"❌ Error general: {str(e)[:100]}")

            finally:
                try:
                    if mail is not None:
                        mail.quit()
                except:
                    pass

            await asyncio.sleep(3)
        
        print(f"\n⏳ [{datetime.now().strftime('%H:%M:%S')}] Ciclo completado. Pausa de 5s...\n")
        await asyncio.sleep(5)

# 🚀 Función principal
async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    
    print("=" * 60)
    print("🤖 BOT DE TELEGRAM INICIADO")
    print("=" * 60)
    print(f"📧 Monitoreando {len(EMAIL_ACCOUNTS)} cuentas")
    print(f"👥 {len(TELEGRAM_CHAT_IDS)} usuarios registrados")
    print(f"💾 Estado guardado en: {STATE_FILE}")
    print("=" * 60 + "\n")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    await revisar_correos()

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())