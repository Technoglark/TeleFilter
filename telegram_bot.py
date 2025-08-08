import telebot
from telebot import types
import time
from gmail_parser import get_service, get_body, getEmails, get_ids
from SpamClassifier import NBC
from deep_translator import GoogleTranslator


def define_str_language(s: str):
    eng_counter = 0
    ru_counter = 0
    for symb in s:
        if 1072 <= ord(symb) <= 1103:
            ru_counter += 1
        elif 97 <= ord(symb) <= 122:
            eng_counter += 1

    if ru_counter > eng_counter:
        return 'ru'
    return 'eng'


print('Bot started...')
BOT_TOKEN = '8286740706:AAHCwzwEGfrga30jZ3j8Ctp4FNyokG3mYWU'
bot = telebot.TeleBot(BOT_TOKEN)

classifier = NBC()
classifier.load_options()

user_gmail = ''

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, "Hello, enter your gmail please: ")
        bot.register_next_step_handler(message, get_gmail)
    else:
        bot.send_message(message.from_user.id, "Please, send command '/start'")
        bot.register_next_step_handler(message, start)

def get_gmail(message):
    global user_gmail
    user_gmail = message.text
    bot.send_message(message.from_user.id, "To start checking your gmail send command '/start_checking': ")
    bot.register_next_step_handler(message, start_checking)

def start_checking(message):
    if message.text == '/start_checking':
        bot.send_message(message.from_user.id, "Starting checking your gmail...")
        service = get_service(user_gmail)
        last_id = get_ids(service, quantity=1)[0]['id']
        while True:
            current_id = get_ids(service, quantity=1)[0]['id']
            if current_id != last_id:
                bot.send_message(message.from_user.id, "You have a new message!")
                new_message = getEmails(service, quantity=1)[0]



                message_text = new_message['text']
                if define_str_language(message_text) == 'ru':
                    message_text = GoogleTranslator(sourse='ru', target='en').translate(message_text)
                spam_prediction = classifier.predict([message_text])


                bot_message = f"📚 Subject: {new_message['subject']}\n 🤷‍♂Sender: {new_message['sender']} \n ✉️ Text: {new_message['text']}"
                bot.send_message(message.from_user.id, bot_message)
                '''
                bot.send_message(message.from_user.id, f"Subject: {new_message['subject']}")
                bot.send_message(message.from_user.id, f"️ Sender: {new_message['sender']}")
                bot.send_message(message.from_user.id, f" Text: {new_message['text']}")
                '''
                if spam_prediction[0] == 0:
                    bot.send_message(message.from_user.id, f"✅ Not a spam")
                else:
                    bot.send_message(message.from_user.id, f"🚫 Spam!")

                last_id = current_id

            time.sleep(5)
    else:
        bot.send_message(message.from_user.id, "Send a command '/start_checking', please")
        bot.register_next_step_handler(message, start_checking)


bot.polling(none_stop=True, interval=0)