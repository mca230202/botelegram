  
import poplib
from email import parser
import time
from telegram import Bot
import asyncio
import re
import sys

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
    "5910916435", "1791117148", "5695562269", "1021277549",
    "5836513962", "5850828120", "6767314967", "1137438609", "7360240142",
    "5470876128","1451249740","1111737214","7673978510","5850909591",
    "1581029678","6160541808","1227729423","5987153884","7651831770","8370693961",
    "1579793937","6693922368","7771540264","8367272724","6661729470","6760211269",
    "5593201016","1392235267","8364691286","8276764044","1111737214","8410501491","5695604052",
    "880945915","8281293369","1540389579","8137172507","8417576668","7336498086"
]

# 🔹 Crear el bot de Telegram
bot = Bot(token=TELEGRAM_TOKEN)

# 🔄 Revisión de correos
async def revisar_correos():
    while True:
        for EMAIL_ACCOUNT, PASSWORD in EMAIL_ACCOUNTS:
            mail = None
            try:
                print(f"🔍 Conectando al servidor POP3 para {EMAIL_ACCOUNT}...")
                mail = poplib.POP3_SSL(POP3_SERVER, PORT, timeout=30)

                mail.user(EMAIL_ACCOUNT)
                mail.pass_(PASSWORD)

                num_messages = len(mail.list()[1])
                print(f"📩 Correos encontrados: {num_messages}")

                for i in range(num_messages, 0, -1):
                    raw_email = b"\n".join(mail.retr(i)[1])
                    email_message = parser.Parser().parsestr(raw_email.decode(errors='replace'))

                    content = ""
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            if part.get_content_type() in ["text/plain", "text/html"]:
                                content += (part.get_payload(decode=True) or b"").decode(errors='replace')
                    else:
                        content = (email_message.get_payload(decode=True) or b"").decode(errors='replace')

                    print(f"\n🔍 Correo de: {email_message.get('from')}")
                    print(f"📅 Fecha: {email_message.get('date')}")
                    print(f"📩 Asunto: {email_message.get('subject')}")
                    print(f"✉️ Contenido: {content[:500]}...")

                    boton_match = re.search(r'enviada desde.*?(https?://[^\s"\'<>]+)', content, re.IGNORECASE | re.DOTALL)
                    boton_match2 = re.search(r'<a[^>]+href=["\'](https?://[^\s"\'<>]+)["\'][^>]*>\s*Obtener código\s*</a>', content, re.IGNORECASE)

                    if boton_match:
                        url_encontrado = boton_match.group(1)
                        mensaje = f"📬 Nuevo correo detectado en {EMAIL_ACCOUNT}!\n🔗 URL del botón: {url_encontrado}"
                        for chat_id in TELEGRAM_CHAT_IDS:
                            await bot.send_message(chat_id=chat_id, text=mensaje)
                    elif boton_match2:
                        url_encontrado2 = boton_match2.group(1)
                        mensaje2 = f"📬 Nuevo correo detectado en {EMAIL_ACCOUNT}!\n🔗 URL del botón: {url_encontrado2}"
                        for chat_id in TELEGRAM_CHAT_IDS:
                            await bot.send_message(chat_id=chat_id, text=mensaje2)
                    else:
                        print("⚠️ No se encontró el link del botón, no se enviará mensaje.")

            except poplib.error_proto as e:
                # Errores POP3 (p.ej. AUTH inválido): NO enviar a Telegram
                print(f"⛔ POP3 error en {EMAIL_ACCOUNT}: {e}")

            except Exception as e:
                # Cualquier otro error: NO enviar a Telegram
                print(f"❌ Error con {EMAIL_ACCOUNT}: {e}")

            finally:
                # Cerrar conexión si llegó a crearse
                try:
                    if mail is not None:
                        mail.quit()
                except Exception:
                    pass

            # pequeña pausa entre cuentas para no martillar el servidor
            await asyncio.sleep(5)
async def main():
    await revisar_correos()

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())