import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
import pickle
import telebot
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Dane z Twojego "sejfu" (.bashrc)
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = telebot.TeleBot(TOKEN)

# Zakres dostępu do Gmaila
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    # Plik token.pickle przechowuje dostęp po pierwszej autoryzacji
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # KONFIGURACJA POD SERWER:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES,
                redirect_uri='https://localhost' # To pozwoli nam wyciągnąć kod z paska adresu
            )
            auth_url, _ = flow.authorization_url(prompt='consent')

            print("-" * 50)
            print(f'1. Otwórz ten link w przeglądarce:\n{auth_url}')
            print("-" * 50)
            print('2. Zaloguj się i zaakceptuj uprawnienia.')
            print('3. Zostaniesz przekierowany na stronę błędu (localhost).')
            print('4. SKOPIUJ całe "code=..." z paska adresu przeglądarki.')
            print("-" * 50)

            code = input('Wklej tutaj skopiowany kod (wszystko po code=): ')
            flow.fetch_token(code=code)
            creds = flow.credentials

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def main():
    try:
        service = get_gmail_service()
        # Szukamy maili od nju mobile
        results = service.users().messages().list(userId='me', q='from:nju@njumobile.pl').execute()
        messages = results.get('messages', [])

        if not messages:
            bot.send_message(CHAT_ID, "🛡️ Lupus: Sprawdziłem pocztę. Brak nowych faktur od nju.")
        else:
            bot.send_message(CHAT_ID, f"🛡️ Lupus: Znaleziono {len(messages)} wiadomości od nju!")

    except Exception as e:
        # Jeśli CHAT_ID jest poprawne, błąd dostaniesz na Telegram
        print(f"Błąd: {e}")
        bot.send_message(CHAT_ID, f"❌ Lupus błąd: {str(e)}")

if __name__ == "__main__":
    main()