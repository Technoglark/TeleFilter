from operator import truediv

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import pickle
import os.path
import base64
import email
from bs4 import BeautifulSoup
import lxml
import time


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_body(payload):
    if 'parts' in payload:
        for part in payload.get('parts'):
            body_data = get_body(part)
            if body_data:
                return body_data
    elif 'body' in payload and 'data' in payload['body']:
        mime_type = payload.get('mimeType', '')
        if 'text/plain' in mime_type or 'text/html' in mime_type:
            return payload['body']['data']
    return None

def get_service(email: str, TOKEN_DIR = 'tokens'):
    creds = None
    if not os.path.exists(TOKEN_DIR):
        os.makedirs(TOKEN_DIR)
        
    token_path = os.path.join(TOKEN_DIR, f"{email}.pickle")
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Не удалось обновить токен для {email}. Пожалуйста, пройдите аутентификацию заново.")
                creds = None

        if not creds:
            try:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            except FileNotFoundError:
                print("Ошибка: файл 'credentials.json' не найден. Убедитесь, что он находится в той же директории.")
                return None

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
        print(f"Аутентификация для {email} прошла успешно. Токен сохранен.")

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f"Произошла ошибка при создании сервиса: {error}")
        return None

    service = build('gmail', 'v1', credentials=creds)
    return service

def getEmails(service = None, quantity: int = 10):


    result = service.users().messages().list(userId='me', maxResults=quantity).execute()
    messages = result.get('messages')

    if not messages:
        print("Письма не найдены.")
        return

    print(messages)

    result: list[dict] = []

    for msg in messages:
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()

        try:
            payload = txt['payload']
            headers = payload['headers']

            subject = "No Subject"
            sender = "No Sender"

            for d in headers:
                if d['name'].lower() == 'subject':
                    subject = d['value']
                if d['name'].lower() == 'from':
                    sender = d['value']

            encoded_data = get_body(payload)

            if not encoded_data:
                print(f"Не удалось найти тело для письма от {sender} с темой '{subject}'")
                continue

            decoded_data = base64.urlsafe_b64decode(encoded_data)

            soup = BeautifulSoup(decoded_data, "lxml")
            body_text = soup.get_text(separator="\n", strip=True)

            result.append({'subject': subject, 'sender': sender, 'text': body_text})

        except Exception as e:
            print(f"Произошла ошибка при обработке письма с id {msg['id']}: {e}")
            import traceback
            traceback.print_exc()
            print('\n')


    return result


def get_ids(service = None, quantity: int = 10):
    result = service.users().messages().list(userId='me', maxResults=quantity).execute()
    messages = result.get('messages')
    return messages










