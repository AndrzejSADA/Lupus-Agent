import os
import imaplib
import email
from email.header import decode_header
import telebot
import schedule
import time

# --- KONFIGURACJA (POBIERANIE TYLKO Z SEJFU) ---
EMAIL = os.environ.get('LUPUS_EMAIL')
PASSWORD = os.environ.get('LUPUS_PwD')
SERVER = "imap.gmail.com"
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
DOSTWCY = ["nju", "nest", "e.on", "pge", "pgnig", "plus"]

def connect_to_mail():
    try:
        if not EMAIL or not PASSWORD:
            print("❌ Błąd: Nie znaleziono LUPUS_EMAIL lub LUPUS_PwD w Sejfie!")
            return None

        mail = imaplib.IMAP4_SSL(SERVER)
        mail.login(EMAIL, PASSWORD)
        print(f"✅ Lupus połączony jako {EMAIL} i skanuje skrzynkę...")

        mail.select("inbox")
        status, messages = mail.search(None, 'UNSEEN')

        for num in messages[0].split():
            res, msg = mail.fetch(num, "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg_obj = email.message_from_bytes(response[1])
                    subject_data = decode_header(msg_obj["Subject"])[0]
                    subject = subject_data[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(subject_data[1] or 'utf-8')

                    if any(d in subject.lower() for d in DOSTWCY):
                        if TOKEN and CHAT_ID:
                            bot = telebot.TeleBot(TOKEN)
                            bot.send_message(CHAT_ID, f"🏦 Lupus znalazł: {subject}")
                            print(f"🚀 Wysłano powiadomienie o: {subject}")
                        else:
                            print("❌ Błąd: Brak danych Telegrama w Sejfie")
        return mail
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")
        return None

def job():
    print(f"🕒 Uruchamiam skanowanie: {time.ctime()}")
    connection = connect_to_mail()
    if connection:
        connection.logout()
        print("🔒 Sesja zakończona bezpiecznie.")

if __name__ == "__main__":
    job() 
    schedule.every().day.at("09:00").do(job)
    print("🚀 Lupus Agent działa w tle i czeka na 09:00...")
    while True:
        schedule.run_pending()
        time.sleep(60)