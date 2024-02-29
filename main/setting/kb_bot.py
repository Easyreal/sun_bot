from telebot.types import KeyboardButton, ReplyKeyboardMarkup



def start_command() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton("/start")
    btn2 = KeyboardButton("❓ Основные команды")
    markup.add(btn1, btn2)
    return markup


def send_contact_command() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = KeyboardButton('ОТПРАВИТЬ СВОЙ КОНТАКТ ☎️', request_contact=True)
    markup.add(btn1)
    return markup


def admin_command() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn0 = KeyboardButton('/help')
    btn1 = KeyboardButton('/show_all_user')
    btn2 = KeyboardButton('/history')
    btn3 = KeyboardButton('/add_admin')
    btn4 = KeyboardButton('/delete_admin')
    markup.add(btn0, btn1, btn2, btn3, btn4)
    return markup



