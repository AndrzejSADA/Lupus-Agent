import os
import pickle
import telebot
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Dane z Twoich zmiennych środowiskowych (z .bashrc)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
bot = telebot.TeleBot(TOKEN)

# Zakres dostępu do Gmaila
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    # Plik token.pickle powstanie po pierwszej autoryzacji
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Używamy Twojego pliku credentials.json (musisz go wgrać!)
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            # Metoda run_local_server nie zadziała na serwerze, używamy konsoli
            creds = flow.run_local_server(port=0, open_browser=False)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def main():
    try:
        service = get_gmail_service()
        # Przykład: Szukamy maili od nju mobile (faktury)
        results = service.users().messages().list(userId='me', q='from:nju@njumobile.pl').execute()
        messages = results.get('messages', [])

        if not messages:
            bot.send_message(CHAT_ID, "🛡️ Lupus: Sprawdziłem pocztę. Brak nowych faktur od nju.")
        else:
            bot.send_message(CHAT_ID, f"🛡️ Lupus: Znaleziono {len(messages)} wiadomości od nju!")

    except Exception as e:
        bot.send_message(CHAT_ID, f"❌ Lupus błąd: {str(e)}")

if __name__ == "__main__":
    main()