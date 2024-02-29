import telebot
from peewee import IntegrityError
from telebot.apihelper import ApiTelegramException
from telebot.types import Message

from main.database.orm_req import (
    create_history,
    create_user,
    get_history,
    get_admins,
    get_all_user,
    update_user_to_admin,
    update_user_to_no_admin,
)
from main.setting.config import BOT_TOKEN, logger, super_admins
from main.setting.kb_bot import send_contact_command, admin_command

bot = telebot.TeleBot(BOT_TOKEN)


def check_user(func):
    def wrapper(message: Message, *args, **kwargs):
        admin = get_admins()
        return func(message=message, admin=admin, *args, **kwargs, )

    wrapper.__name__ = func.__name__
    return wrapper


@bot.message_handler(commands=["start"])
@check_user
def start(message: Message, admin):
    first_name = message.from_user.first_name
    hello_text = f" Привет, {first_name}! Я – бот компании INSIDE BRAND. Рад знакомству!" \
                 f"\n\nГК «INSIDE BRAND» основана в 2018 году на базе объединения " \
                 f"Бренд-консалтингового агентства «SUN» (с 2003г.) и Студии персонального бренд - дизайна «Estudio». " \
                 f"\n\nКоротко о нас. Создавая смыслы, раскрываем лучшее в людях и компаниях!" \
                 f"\n\n1000 + Запусков и реструктуризаций брендов и коммуникаций. ГЕО: Россия, СНГ, Западная Европа, США" \
                 f"\n\nПрезентацию с кейсами можно посмотреть по ссылке: https://disk.yandex.ru/d/VJfpNeEL1Uc53w" \
                 f"\n\n✅ Опиши свою задачу в паре слов или прикрепи бриф. Я сразу же передам это команде."

    if message.from_user.id in admin:
        logger.debug(f"Начало работы админа - {message.from_user.id}")
        hello_text = f"Рад вас приветствовать владец бота {first_name}!\n\n" \
                     f"Я бот-визитка, здесь вы будуте получать информацию о пользователях вашего бота!\n\n" \
                     f"Также сюда будут приходить прикрепленные файлы и фотографии от пользователей!"

        start_markup = admin_command()
    else:
        logger.debug(f"Начало работы пользователем - {message.from_user.id}")
        try:
            create_user(message)
            logger.debug(f"Новый пользователя {message.from_user.id}")
            start_markup = send_contact_command()

        except IntegrityError:
            logger.debug(f"Пользователя {message.from_user.id} уже существует")
            start_markup = send_contact_command()

    bot.send_message(message.chat.id, text=hello_text, reply_markup=start_markup)
    create_history(message)


@bot.message_handler(content_types=['contact'])
@check_user
def get_contact(message: Message, admin):
    logger.debug(f"Отправлен контакт: {message.from_user.id}")
    if message.from_user.id not in admin:
        for tg_id in admin:
            try:
                bot.send_message(tg_id, text=f'Пользователь {message.from_user.id} отправил контакт!')
                bot.send_contact(tg_id, phone_number=message.contact.phone_number,
                                 first_name=message.contact.first_name)
                msg = f"Спасибо! Передал сообщение команде.\n"
                bot.send_message(message.chat.id, msg)
            except ApiTelegramException:
                logger.error(f"Пользователь № {tg_id} не найден")
    else:
        for tg_id in admin:
            try:
                if tg_id != str(message.from_user.id):
                    bot.send_contact(tg_id, phone_number=message.contact.phone_number,
                                     first_name=message.contact.first_name)
            except ApiTelegramException:
                logger.error(f"Пользователь № {tg_id} не найден")


@bot.message_handler(commands=['history'])
@check_user
def history_to_admin(message: Message, admin):
    logger.debug(f"Админ - {message.from_user.id}| команда - /history")
    if message.from_user.id in admin:
        result = get_history()
        with open("history.txt", mode='w') as file:
            file.write(str(result))
        with open("history.txt", mode='r') as file:
            try:
                bot.send_document(message.from_user.id, file)
            except ApiTelegramException:
                bot.send_message(message.chat.id, f"Файл пустой!")
    else:
        return None


@bot.message_handler(commands=['help'])
@check_user
def history_to_admin(message: Message, admin):
    logger.debug(f"Админ - {message.from_user.id}| команда - /help")
    if message.from_user.id in admin:
        text = f"Привет {message.from_user.first_name}! Это снова я, ваш бот\n\nВот что я могу:\n" \
               f"/help - Получить информацию о моей работе!\n" \
               f"/show_all_user - Получить информацию о всех пользователях этого бота!\n" \
               f"/add_admin - Дать пользователю права администратора\n" \
               f"/delete_admin - Лишить админа прав администратора\n" \
               f"/history - Просмотреть историю запросов пользователей!"
        bot.send_message(message.chat.id, text=text)
    else:
        return None


@bot.message_handler(commands=['add_admin'])
def create_admin(message: Message):
    if message.from_user.id in super_admins:
        logger.debug(f"Админ - {message.from_user.id}| команда - /add_admin")
        msg = bot.send_message(message.from_user.id, text=f'Введите id пользователя, для добавления в админы')
        bot.register_next_step_handler(msg, step_1_to_admin)
    else:
        bot.send_message(message.from_user.id, text=f'У вас нет таких прав...')


def step_1_to_admin(message: Message):
    if str(message.text).isnumeric():
        if update_user_to_admin(int(message.text)):
            text = f"Пользователь {message.text} успешно стал админом!"
        else:
            text = f"Пользователь {message.text} уже был админом"
    else:
        text = "Вы ввели не число!"

    bot.send_message(message.from_user.id, text=text)


@bot.message_handler(commands=['delete_admin'])
def delete_admin(message: Message):
    logger.debug(f'{super_admins}')
    if message.from_user.id in super_admins:

        logger.debug(f"Админ - {message.from_user.id}| команда - /delete_admin")
        msg = bot.send_message(message.from_user.id, text=f'Введите id пользователя, для исключения из админов')
        bot.register_next_step_handler(msg, step_1_to_no_user)
    else:
        bot.send_message(message.from_user.id, text=f'У вас нет таких прав...')


def step_1_to_no_user(message: Message):
    if str(message.text).isnumeric():
        if update_user_to_no_admin(int(message.text)):
            text = f"Пользователь {message.text} успешно был исключен из администраторов!"
        else:
            text = f"Пользователь {message.text} не является админом"
    else:
        text = "Вы ввели не число!"

    bot.send_message(message.from_user.id, text=text)


@bot.message_handler(commands=['show_all_user'])
@check_user
def show_all_user(message: Message, admin):
    if message.from_user.id in admin:
        logger.debug(f"Админ - {message.from_user.id}| команда - /show_all_user")
        msg = get_all_user()
        bot.send_message(message.from_user.id, text=f"Список пользователей:\n\n{msg}")
    else:
        return None


@bot.message_handler(content_types=['text'])
@check_user
def support_chat(message: Message, admin):
    if message.from_user.id in admin:
        logger.debug(f"Администратор - {message.from_user.id}; текст - {message.text}")
        for tg_id in admin:
            try:
                if tg_id != message.from_user.id:
                    msg = f"{message.from_user.first_name} отправил(а) сообщение: \n{message.text}"
                    bot.send_message(tg_id, msg)
            except ApiTelegramException:
                logger.error(f"Пользователь № {tg_id} не найден")



    else:
        create_history(message)
        logger.debug(f"Пользователь - {message.from_user.id}; текст - {message.text}")

        for tg_id in admin:
            try:
                bot.forward_message(tg_id, message.chat.id, message.message_id)
            except ApiTelegramException:
                logger.error(f"Пользователь № {tg_id} не найден")
        msg = f"Спасибо! Передал сообщение команде.\nЕсли у тебя приватный профиль, то отправь свой контакт!"
        bot.send_message(message.chat.id, msg)


@bot.message_handler(content_types=['document'])
@check_user
def forward_adm_document(message: Message, admin):
    if message.from_user.id in admin:
        for tg_id in admin:
            try:
                if tg_id != admin:
                    file_info = bot.get_file(message.document.file_id)
                    downloaded_file = bot.download_file(file_info.file_path)
                    msg = f"{message.from_user.first_name} отправил(а) сообщение: \n{message.caption}"
                    bot.send_document(tg_id, downloaded_file, caption=msg)
            except ApiTelegramException:
                logger.error(f"Пользователь № {tg_id} не найден")

    else:
        for tg_id in admin:
            try:
                bot.forward_message(tg_id, message.chat.id, message.message_id)
            except ApiTelegramException:
                logger.error(f"Пользователь № {tg_id} не найден")
        msg = f"Спасибо! Передал сообщение команде.\nЕсли у тебя приватный профиль, то отправь свой контакт!"
        bot.send_message(message.chat.id, msg)


@bot.message_handler(content_types=['photo'])
@check_user
def forward_adm_photo(message: Message, admin):
    if message.from_user.id in admin:
        for tg_id in admin:
            try:
                if tg_id != message.from_user.id:
                    fileID = message.photo[-1].file_id
                    file_info = bot.get_file(fileID)
                    photo = bot.download_file(file_info.file_path)
                    msg = f"{message.from_user.first_name} отправил(а) сообщение: \n{message.caption}"
                    bot.send_photo(tg_id, photo, caption=msg)
            except ApiTelegramException:
                logger.error(f"Пользователь № {tg_id} не найден")

    else:
        for tg_id in admin:
            try:
                bot.forward_message(tg_id, message.chat.id, message.message_id)
            except ApiTelegramException:
                logger.error(f"Пользователь № {tg_id} не найден")
        msg = f"Спасибо! Передал сообщение команде.\nЕсли у тебя приватный профиль, то отправь свой контакт!"
        bot.send_message(message.chat.id, msg)
