import os
import imaplib
import email
from email.header import decode_header
import telebot

# --- KONFIGURACJA (POBIERANIE Z SEJFU) ---
EMAIL = "andrzej.skrucha@gmail.com"
# Zmieniamy GMAIL_PASS na Twoją nazwę z Bash:
PASSWORD = os.environ.get('LUPUS_PwD')
SERVER = "imap.gmail.com"

# Dane Telegrama (nazwy są zgodne z Twoim grepem)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
# Twoja lista dostawców
DOSTWCY = ["nju", "nest", "e.on", "pge", "pgnig", "plus"]

def connect_to_mail():
    try:
        # Sprawdzamy czy pobrano dane z Sejfu
        if not EMAIL or not PASSWORD:
            print("❌ Błąd: Nie znaleziono danych logowania w Sejfu (GMAIL_USER/GMAIL_PASS)")
            return None

        mail = imaplib.IMAP4_SSL(SERVER)
        mail.login(EMAIL, PASSWORD)
        print("✅ Lupus połączony i skanuje skrzynkę...")

        mail.select("inbox")
        status, messages = mail.search(None, 'UNSEEN')

        for num in messages[0].split():
            res, msg = mail.fetch(num, "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg_obj = email.message_from_bytes(response[1])

                    # Odczytujemy temat
                    subject_data = decode_header(msg_obj["Subject"])[0]
                    subject = subject_data[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(subject_data[1] or 'utf-8')

                    # Sprawdzamy czy pasuje do listy
                    if any(d in subject.lower() for d in DOSTWCY):
                        TOKEN = os.environ.get('TELEGRAM_TOKEN')
                        CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

                        if TOKEN and CHAT_ID:
                            bot = telebot.TeleBot(TOKEN)
                            bot.send_message(CHAT_ID, f"🏦 Lupus znalazł: {subject}")
                            print(f"🚀 Wysłano powiadomienie o: {subject}")
                        else:
                            print("❌ Błąd: Brak TELEGRAM_TOKEN lub TELEGRAM_CHAT_ID w Sejfu")

        return mail
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return None

if __name__ == "__main__":
    connection = connect_to_mail()
    if connection:
        connection.logout()
        print("🔒 Sesja zakończona bezpiecznie.")