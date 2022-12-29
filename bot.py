import telebot
import requests

# укажите токен, полученный у @BotFather
TOKEN = "5558743958:AAGYZ3ahoK_4NpjKEcHPveJZdCjrBZshBj0"

# создаем бота
bot = telebot.TeleBot(TOKEN)

# словарь активных курьеров (ключ - id чата, значение - номер телефона)
couriers = {}

# словарь заказов (ключ - id заказа, значение - id чата курьера, который взял заказ)
orders = {}


# функция для проверки номера телефона через API CRM
def check_phone(phone):
    # укажите URL и параметры для запроса к API CRM
    url = "https://crm.example.com/api/check_phone"
    params = {"phone": phone}

    # отправляем запрос к API CRM
    r = requests.get(url, params=params)

    # проверяем результат
    if r.status_code == 200:
        data = r.json()
        if data["is_courier"]:
            return True


# обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    # проверяем, является ли пользователь курьером
    if check_phone(message.text):
        # добавляем курьера в список активных курьеров
        couriers[message.chat.id] = message.text
        # отправляем сообщение с приветствием
        bot.send_message(message.chat.id, "Добро пожаловать, курьер! Вы можете получать заказы через бота.")
    else:
        # отправляем сообщение с ошибкой
        bot.send_message(message.chat.id, "Извините, вы не являетесь курьером.")


# обработчик новых заказов
@bot.message_handler(func=lambda message: message.text.startswith("Новый заказ:"))
def new_order(message):
    # парсим id заказа из текста сообщения
    order_id = message.text.split(":")[1].strip()
    # формируем клавиатуру с кнопками "Принять" и "Отказать"
    keyboard = telebot.types.InlineKeyboardMarkup()
    accept_button = telebot.types.InlineKeyboardButton(text="Принять", callback_data=f"accept_{order_id}")
    decline_button = telebot.types.InlineKeyboardButton(text="Отказать", callback_data=f"decline_{order_id}")
    keyboard.add(accept_button, decline_button)

    # отправляем сообщение с заказом и кнопками
    bot.send_message(message.chat.id, "Новый заказ:", reply_markup=keyboard)


# обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def accept_order(call):
    # парсим id заказа из данных кнопки
    order_id = call.data.split("_")[1]
    # проверяем, не взят ли уже этот заказ
    if order_id not in orders:
        # добавляем заказ в список взятых заказов
        orders[order_id] = call.message.chat.id
        # отправляем сообщение о том, что заказ принят
        bot.send_message(call.message.chat.id, "Заказ принят!")
    else:
        # отправляем сообщение об ошибке
        bot.send_message(call.message.chat.id, "Извините, этот заказ уже взят другим курьером.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("decline_"))
def decline_order(call):
    # отправляем сообщение о том, что заказ отклонен
    bot.send_message(call.message.chat.id, "Заказ отклонен.")


# функция для загрузки фото с получателем посылки
def upload_photo(chat_id, photo):
    # укажите URL и параметры для запроса к API webapps
    url = "https://webapps.example.com/api/upload_photo"
    data = {"chat_id": chat_id, "photo": photo}

    # отправляем запрос к API webapps
    r = requests.post(url, data=data)

    # проверяем результат
    if r.status_code == 200:
        return True
    return False


# обработчик команды /finish
@bot.message_handler(commands=['finish'])
def finish(message):
    # проверяем, что курьер взял какой-то заказ
    if message.chat.id in orders:
        order_id = orders[message.chat.id]
        # проверяем, что фото приложено
        if message.photo:
            # загружаем фото через API webapps
            if upload_photo(message.chat.id, message.photo[-1].file_id):
                # удаляем заказ из списка взятых заказов
                del orders[message.chat.id]
                # отправляем сообщение о том, что заказ доставлен
                bot.send_message(message.chat.id, "Заказ успешно доставлен!")
            else:
                # отправляем сообщение об ошибке
                bot.send_message(message.chat.id, "Извините, произошла ошибка при загрузке фото.")
        else:
            # отправляем сообщение об ошибке
            bot.send_message(message.chat.id, "Извините, необходимо приложить фото с получателем посылки.")
    else:
        # отправляем сообщение об ошибке
        bot.send_message(message.chat.id, "Извините, вы не взяли ни одного заказа.")


# функция для трансляции статуса заказа в канал
def send_status(order_id, status):
    # укажите URL и параметры для запроса к API webapps
    url = "https://webapps.example.com/api/send_status"
    data = {"order_id": order_id, "status": status}

    # отправляем запрос к API webapps
    r = requests.post(url, data=data)

    # проверяем результат
    if r.status_code == 200:
        return True
    return False


# функция для отправки сообщения в канал
def send_message(text):
    # укажите URL и параметры для запроса к API webapps
    url = "https://webapps.example.com/api/send_message"
    data = {"text": text}

    # отправляем запрос к API webapps
    r = requests.post(url, data=data)

    # проверяем результат
    if r.status_code == 200:
        return True
    return False


# добавляем вызовы функций в обработчики кнопок
@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def accept_order(order_id, call):
    # тут оставим те же строки, что и ранее
    # ...
    # транслируем статус "принят" в канал
    send_status(order_id, "принят")


@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def accept_order(order_id, call):
    # тут оставим те же строки, что и ранее
    # ...
    # транслируем статус "принят" в канал
    send_status(order_id, "принят")


@bot.callback_query_handler(func=lambda call: call.data.startswith("decline_"))
def decline_order(call):
    # парсим id заказа из данных кнопки
    order_id = call.data.split("_")[1]
    # транслируем статус "отклонен" в канал
    send_status(order_id, "отклонен")


# обработчик команды /finish
@bot.message_handler(commands=['finish'])
def finish(order_id, message):
    # тут оставим те же строки, что и ранее
    # ...
    # транслируем статус "доставлен" в канал
    send_status(order_id, "доставлен")


bot.polling()
