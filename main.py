import pymysql
import telebot
import os
from config import TOKEN
from _mysql.requests import get_photo, count_photos, get_data, get_date
import time

bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    cht = message.chat.id
    bot.send_message(cht, f'Вітаю, <b>{message.from_user.username}</b>!\nСписок всіх товарів - <b>/list</b>\nЗамовити товар - <b>/offer</b>', parse_mode='HTML')

@bot.message_handler(commands=['list'])
def get_list(message):
    cht = message.chat.id
    try:
        get_photo()
        data_list = get_data()

        if data_list:
            data_text = ""
            for i, data in enumerate(data_list):
                data_text += f"{data[0]}. {data[1]}\n"

            initial_message = bot.send_message(cht, 'Для того щоб переглянути товар детальніше, надішліть номер товару\n<b><i>Список надішлеться через: </i></b>', parse_mode='HTML')
            k = 8
            for i in range(7):
                k -= 1
                bot.edit_message_text(chat_id=cht, message_id=initial_message.message_id, text=f'Для того щоб переглянути товар детальніше, надішліть номер товару\n<b><i>Список надішлеться через: {k}</i></b>', parse_mode='HTML')
                time.sleep(1)
            bot.edit_message_text(chat_id=cht, message_id=initial_message.message_id, text=data_text)

        else:
            bot.send_message(cht, "Немає даних про товари.")

    except Exception as ex:
        bot.send_message(cht, str(ex))

@bot.message_handler(commands=['offer'])
def get_item(message):
    cht = message.chat.id
    msg = bot.send_message(cht, "Будь ласка введіть номер товару, який хочете замовити\nСписок усіх товарів - <b>/list</b>", parse_mode='HTML')
    bot.register_next_step_handler(msg, post_offer)

def post_offer(message):
    cht = message.chat.id
    user_data[cht] = {'item': message.text}
    msg = bot.send_message(cht, "Будь ласка, введіть ПІБ:")
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text
    msg = bot.send_message(chat_id, "Тепер введіть адресу доставки:")
    bot.register_next_step_handler(msg, get_address)

def get_address(message):
    chat_id = message.chat.id
    user_data[chat_id]['address'] = message.text
    msg = bot.send_message(chat_id, "Реквізити для оплати:\n<b><pre>1111 2222 3333 4444</pre></b>\nПісля оплати, надішліть, будь ласка, фото квитанції про здійснення оплати", parse_mode='HTML')
    bot.register_next_step_handler(msg, get_receipt)

def get_receipt(message):
    cht = message.chat.id
    chat_id = message.chat.id
    if message.photo:
        user_data[chat_id]['receipt'] = message.photo[-1].file_id

        user_name = message.from_user.username
        item = user_data[chat_id]['item']
        name = user_data[chat_id]['name']
        address = user_data[chat_id]['address']
        receipt_file_id = user_data[chat_id]['receipt']

        photo_info = bot.get_file(receipt_file_id)
        downloaded_file = bot.download_file(photo_info.file_path)
        photo_path = f"receipts/offer.jpg"

        with open(photo_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        user_data.pop(chat_id, None)

        try:
            connection = pymysql.connect(
                host='sql8.freemysqlhosting.net',
                user='sql8641333',
                password='SrRcPImvQT',
                database='sql8641333',
                port=3306
            )
            cursor = connection.cursor()

            for i in range(len(get_data())):
                if item == str(get_data()[i][0]):
                    item = str(get_data()[i][1])

            with open('receipts/offer.jpg', 'rb') as photo:
                cursor.execute("INSERT INTO offers (time, item, username, name, address, receipt) VALUES (%s, %s, %s, %s, %s, %s)", (get_date(), item, user_name, name, address, photo))
            try:
                # cursor.execute("SELECT * FROM offers")
                # data = cursor.fetchall()
                textToTelegram = f'{get_date()} <b>Нова заявка!</b>\n@{user_name}\n{item}\n{address}'
                    
                with open('receipts/offer.jpg', 'rb') as photo:
                    bot.send_photo(1001173176, photo, textToTelegram, parse_mode='HTML')


                bot.send_message(chat_id, "Дякую, заявку було надіслано! Незабаром з вами зв'яжеться продавець")
            except Exception as ex:
                bot.send_message(cht, ex)
        except Exception as ex:
            bot.send_message(chat_id, str(ex))

@bot.message_handler(content_types=['text'])
def text(message):
    cht = message.chat.id
    for i in range(len(get_data())):
        if message.text == str(get_data()[i][0]):
            with open(f'from-db-images/{message.text}.jpg', 'rb') as photo:
                caption = f'{get_data()[i][1]}\nЦіна: ₴{get_data()[i][2]}'
                bot.send_photo(cht, photo, caption)

bot.polling()