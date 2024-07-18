# Test Token = 5873982989:AAHQopiGJ17LQJ-GDxSu6pbA9whLaVBhCAA
# Work Token = 6074005468:AAHHoEjN-OKJ-v0x4HbXtELECQAX6rSFiR8

import telebot
import re
from telebot import types
import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.http import MediaFileUpload
import os



bot = telebot.TeleBot('token')
user_dict = {}
count_family_stop = {}
count_family = {}


class User:
    def __init__(self, name):
        self.username = None
        self.name = name
        self.telephone = None
        self.idphoto = None
        self.pvr = None
        self.list_request = None
        self.family_members_dict = {}
        self.family_members_split = None
        self.file_photo_info = None
        self.string_for_write = ''

#@bot.message_handler(content_types=['text', 'document', 'audio'])
@bot.message_handler(commands=['start'])
def start(message):
    try:
        if message.text == '/start':
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button1 = types.KeyboardButton('🧾Оформить заявку')
            markup.add(button1)
            bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name} {message.from_user.last_name}! \n"
                             f"Для получения помощи(одежда, обувь, бытовые приборы, посуда, игрушки, детские принадлежности, лекарства), заполните, пожалуйста, анкету. \nДля этого нажмите кнопку 'Оформить заявку'",
                             reply_markup=markup)
        else:
            bot.send_message(message.from_user.id, 'Напишите /start или /help')
    except Exception as e:
        bot.send_message(message, 'Ошибка!')
        print(f'start exception: {e.args}')

@bot.message_handler(commands=['help'])
def help(message):
    try:
        if message.text == '/help':
            bot.send_message(message.chat.id, 'По всем вопросам: https://t.me/ovoronzova')
        else:
            bot.send_message(message.from_user.id, 'Напишите /start')
    except Exception as e:
        bot.send_message(message, 'Ошибка!')
        print(f'help exception: {e.args}')

#ловим нажатие на кнопки
@bot.message_handler(content_types=['text'])
def button_text_handler(message):
    try:
        keyboard_del = types.ReplyKeyboardRemove()
        if (message.text == "🧾Оформить заявку"):
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
            button1 = types.KeyboardButton('✅Согласен')
            button2 = types.KeyboardButton('❌Не согласен')
            markup.add(button1, button2)
            bot.send_message(message.from_user.id, '❗️ Обязательные пункты, чтобы оформить заявку: ФИО, телефон и фото семьи(без него заявка не принимается).', reply_markup=markup)
            #bot.register_next_step_handler(message, request_agr_disagr)

        elif (message.text == "✅Согласен"):
            bot.send_message(message.from_user.id, '❓️ Напишите ФИО заявителя.', reply_markup=keyboard_del)
            bot.register_next_step_handler(message, get_name)
        elif (message.text == "❌Не согласен"):
            bot.send_message(message.from_user.id, 'Напишите /start, чтобы начать заново',reply_markup=keyboard_del)
            bot.register_next_step_handler(message, start)
        else:
            bot.send_message(message.from_user.id, 'Нажмите, нужную кнопку. Помните! Без фото зявка НЕ принимается')
    except Exception as e:
        bot.send_message(message, 'Ошибка!')
        print(f'button_text_handler exception: {e.args}')

#Получаем имя
def get_name(message):
    try:
        #global name
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        user_dict[chat_id] = user

        keyboard = types.InlineKeyboardMarkup(row_width=2)  # наша клавиатура
        key_save_name = types.InlineKeyboardButton(text='✅Сохранить',
                                               callback_data='save_name')  # кнопка сохранить имя
        key_rewrite_name = types.InlineKeyboardButton(text='❌Изменить',
                                                  callback_data='rewrite_name')  # кнопка переписать имя
        keyboard.add(key_save_name, key_rewrite_name)
        bot.send_message(message.chat.id,
                         text=f"Вы внесли ФИО: {user_dict[chat_id].name}",
                         reply_markup=keyboard)
    except Exception as e:
        bot.send_message(message, 'Ошибка!')
        print(f'get_name exception: {e.args}')

#получаем телефон
def get_telephone(message):
    try:
        chat_id = message.chat.id
        telephone = message.text
        user = user_dict[chat_id]
        user.telephone = telephone
        user.username = message.from_user.username

        keyboard = types.InlineKeyboardMarkup(row_width=2)  # наша клавиатура
        key_save_telephone = types.InlineKeyboardButton(text='✅Сохранить',
                                                   callback_data='save_telephone')  # кнопка сохранить имя
        key_rewrite_telephone = types.InlineKeyboardButton(text='❌Изменить',
                                                      callback_data='rewrite_telephone')  # кнопка переписать имя
        keyboard.add(key_save_telephone, key_rewrite_telephone)
        bot.send_message(message.chat.id,
                         text=f"Вы внесли телефон: {user_dict[chat_id].telephone}",
                         reply_markup=keyboard)
    except Exception as e:
        bot.send_message(message, 'Ошибка!')
        print(f'get_telephone exception: {e.args}')

#ловим все фото
@bot.message_handler(content_types=['photo'])
def handle_photo(call_photo):
    try:
        chat_id = call_photo.chat.id
        idphoto = call_photo.photo[0].file_id

        file_photo_info = bot.get_file(call_photo.photo[len(call_photo.photo) - 1].file_id)

        user = user_dict[chat_id]
        user.idphoto = idphoto
        user.file_photo_info = file_photo_info
        get_photo(chat_id)
    except Exception as e:
        bot.send_message(chat_id, 'Ошибка!')
        print(f'handle_photo exception: {e.args}')

#получаем фото
def get_photo(message):
    try:
        chat_id = message
        keyboard = types.InlineKeyboardMarkup(row_width=2)  # наша клавиатура
        key_save_photo = types.InlineKeyboardButton(text='✅Сохранить',
                                                   callback_data='save_photo')  # кнопка сохранить имя
        key_rewrite_photo = types.InlineKeyboardButton(text='❌Изменить',
                                                      callback_data='rewrite_photo')  # кнопка переписать имя
        keyboard.add(key_save_photo, key_rewrite_photo)
        #photo_=open('port.png','rb')
        bot.send_photo(message, user_dict[chat_id].idphoto, reply_markup=keyboard)
    except Exception as e:
        bot.send_message(message, 'Ошибка!')
        print(f'get_photo exception: {e.args}')










#получаем ПВР
def get_PVR(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        pvr = message.text
        user.pvr = pvr

        keyboard = types.InlineKeyboardMarkup(row_width=2)  # наша клавиатура
        key_save_pvr = types.InlineKeyboardButton(text='✅Сохранить',
                                                    callback_data='save_pvr')  # кнопка сохранить имя
        key_rewrite_pvr = types.InlineKeyboardButton(text='❌Изменить',
                                                       callback_data='rewrite_pvr')  # кнопка переписать имя
        keyboard.add(key_save_pvr, key_rewrite_pvr)
        bot.send_message(message.chat.id,
                         text=f"Вы внесли {user.pvr}", reply_markup=keyboard)  # ,reply_markup=keyboard

    except Exception as e:
        bot.send_message(message, 'Ошибка!')
        print(f'get_photo exception: {e.args}')

#Получаем информацию о членах семьи
def get_family_members(message):
    try:
        chat_id = message.chat.id
        family_members = message.text

        family_members_dict = {}

        #заменяем все пунктуационные знаки на точку с запятой и заносим в список
        family_members_replace = re.sub(r'[.,"\'-?:!]', ';', family_members)
        family_members_split = family_members_replace.split(";")
        #заносим family_members_split(членов семьи) в словарь user
        user = user_dict[chat_id]
        user.family_members_split = family_members_split
        #заносим каждого члена семьи в словарь family_members_dict
        for member in family_members_split:
            family_members_dict[member] = ''
        user.family_members_dict = family_members_dict


        count_family_stop[chat_id] = len(user.family_members_split)
        count_family[chat_id] = 0
        #включаем клавиатуру сохранить и изменить выводим то, что написал пользователь
        keyboard = types.InlineKeyboardMarkup(row_width=2)  # наша клавиатура
        key_save_family_members = types.InlineKeyboardButton(text='✅Сохранить',
                                               callback_data='save_family_members')  # кнопка сохранить имя
        key_rewrite_family_members = types.InlineKeyboardButton(text='❌Изменить',
                                                  callback_data='rewrite_family_members')  # кнопка переписать имя
        keyboard.add(key_save_family_members, key_rewrite_family_members)
        bot.send_message(message.chat.id,
                         text=f"Вы внесли: {user_dict[chat_id].family_members_split}",
                         reply_markup=keyboard)
    except Exception as e:
        bot.send_message(message, 'Ошибка!')
        print(f'get_family exception: {e.args}')

#получаем информацию о каждом члене семьи
def get_every_member_family(message, member):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]

        #global family_members_dict
        current_member = message.text
        #family_members_dict[member]=current_member

        user.family_members_dict[member]=current_member

        keyboard = types.InlineKeyboardMarkup(row_width=2)  # наша клавиатура
        key_save_every_member_family = types.InlineKeyboardButton(text='✅Сохранить',
                                                   callback_data=f'save_family_members_{member}')
        key_rewrite_every_member_family = types.InlineKeyboardButton(text='❌Изменить',
                                                      callback_data=f'rewrite_family_members_{member}')
        keyboard.add(key_save_every_member_family, key_rewrite_every_member_family)
        bot.send_message(message.chat.id,
                         text=f"Вы внесли {member}: {current_member}",reply_markup=keyboard)#,reply_markup=keyboard
    except Exception as e:
        bot.send_message(message, 'Ошибка!')
        print(f'get_every_member exception: {e.args}')

#получаем город
def get_request(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        list_request = message.text
        user.list_request = list_request

        keyboard = types.InlineKeyboardMarkup(row_width=2)  # наша клавиатура
        key_save_request = types.InlineKeyboardButton(text='✅Сохранить',
                                                   callback_data='save_request')  # кнопка сохранить имя
        key_rewrite_request = types.InlineKeyboardButton(text='❌Изменить',
                                                      callback_data='rewrite_request')  # кнопка переписать имя
        keyboard.add(key_save_request, key_rewrite_request)
        bot.send_message(message.chat.id,
                         text=f"Вы внесли : {user.list_request}",
                         reply_markup=keyboard)
    except Exception as e:
        bot.send_message(message, 'Ошибка!')
        print(f'get_request exception: {e.args}')

#выводим всю информацию
def all_information(message):
    try:
        chat_id = message
        keyboard = types.InlineKeyboardMarkup(row_width=2)  # наша клавиатура
        key_save_info = types.InlineKeyboardButton(text='✅Сохранить',
                                                   callback_data='save_info')  # кнопка сохранить имя
        key_rewrite_info = types.InlineKeyboardButton(text='❌Изменить',
                                                      callback_data='rewrite_info')  # кнопка переписать имя
        keyboard.add(key_save_info, key_rewrite_info)
        #photo_=open('port.png','rb')
        bot.send_message(message,
                         text=f"Введенная вами информация.\n\nФИО: {user_dict[chat_id].name}; \nТелефон: {user_dict[chat_id].telephone}; \nПВР: {user_dict[chat_id].pvr}; \nЧлены семьи:\n{user_dict[chat_id].family_members_dict};\nСписок запроса: {user_dict[chat_id].list_request}")
        bot.send_photo(message, user_dict[chat_id].idphoto, reply_markup=keyboard)
    except Exception as e:
        bot.send_message(message, 'Ошибка!')
        print(f'all_information exception: {e.args}')


def make_line(user, link_download_file):
    try:
        info = user.family_members_dict
        for key, value in info.items():
            #print(key, ":", value)
            user.string_for_write += f'{key} : {value}'
            user.string_for_write += '\n'
        # print(list_dict)
        info_save = [user.username, user.name, user.telephone, user.pvr, user.string_for_write, user.list_request, link_download_file]
        return info_save
    except Exception as e:
        print(f'make_line exception: {e.args}')

def save_info_to_GoogleSheet(message):
    try:
        chat_id = message
        user = user_dict[chat_id]
        # авторизация к гугл-таблице
        Spread_serv = autoriz()
        # ID таблицы
        spreadsheetId = Spread_serv[0]
        service = Spread_serv[1]
        driveService = Spread_serv[2]
        # Определяем ID листа
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheetId).execute()
        sheetList = spreadsheet.get('sheets')
        # ID листа
        sheetId = sheetList[0]['properties']['sheetId']

        #скачивание фото из Telegram на локальное хранилище и запись имени файла в переменную file_name
        file_name = download_photo_file(user.file_photo_info, chat_id)
        #загрузка файла в GoogleDrive и запись ссылки на фото в переменную link_download_file
        link_download_file = files(driveService, file_name, chat_id)

        #читаем таблицу
        read_spreadseet = read_sheet(service, spreadsheetId)
        #вычисляем номер свободной строки
        if 'values' in read_spreadseet:
            number_of_lines_written = len(read_spreadseet['values'])
        else:
            number_of_lines_written = 0

        line_for_write = make_line(user, link_download_file)
        #добавляем данные в сбодную строку
        add_to_spreadsheet(line_for_write, number_of_lines_written, spreadsheetId, sheetId, service)
        #удаление фото
        delete_local_file(file_name)
        user_dict.pop(chat_id)
    except Exception as e:
        bot.send_message(message, 'Ошибка!')
        print(f'save_info_to_GoogleSheet exception: {e.args}')


@bot.callback_query_handler(func=lambda call: call.data == 'save_name' or call.data == 'rewrite_name')
def callback_inline_name(call):
    try:
        keyboard_del = types.ReplyKeyboardRemove()
        if call.data == 'save_name':
            bot.answer_callback_query(callback_query_id=call.id, text="Сохранено!")
            bot.send_message(call.message.chat.id, '❓️ Напишите ваш телефон для контакта.',reply_markup=keyboard_del)
            bot.register_next_step_handler(call.message, get_telephone)
        # перезапись ФИО
        elif call.data == 'rewrite_name':
            bot.answer_callback_query(callback_query_id=call.id)
            bot.send_message(call.message.chat.id, '❓️ Напишите ФИО заявителя.', reply_markup=keyboard_del)
            bot.register_next_step_handler(call.message, get_name)
    except Exception as e:
        bot.send_message(call.message.chat.id, 'Ошибка!')
        print(f'callback_inline_name exception: {e.args}')


@bot.callback_query_handler(func=lambda call: call.data == 'save_telephone' or call.data == 'rewrite_telephone')
def callback_inline_telephone(call):
    try:
        # сохранение телефона и запрос фото семьи
        if call.data == 'save_telephone':
            bot.answer_callback_query(callback_query_id=call.id, text="Сохранено!")
            bot.send_message(call.message.chat.id,
                             '❓️ Отправьте ваше фото с семьей во весь рост.\n🚩️ ВНИМАТЕЛЬНО, заявка без фото НЕ принимается.')
        # перезапись телефона
        elif call.data == 'rewrite_telephone':
            bot.answer_callback_query(callback_query_id=call.id)
            bot.send_message(call.message.chat.id, '❓️ Напишите ваш телефон для контакта.')
            bot.register_next_step_handler(call.message, get_telephone)
    except Exception as e:
        bot.send_message(call.message.chat.id, 'Ошибка!')
        print(f'callback_inline_telephone exception: {e.args}')

@bot.callback_query_handler(func=lambda call: call.data == 'save_photo' or call.data == 'rewrite_photo')
def callback_inline_photo(call):
    try:
        #сохранение фото и запрос на членов семьи
        if call.data == 'save_photo':
            bot.answer_callback_query(callback_query_id=call.id, text="Сохранено!")
            bot.send_message(call.message.chat.id, '❓️ Напишите название Вашего ПВР(Звезда, Водник, Лукоморье) и номер комнаты! \n🚩️ Пример: Звезда, 12')
            bot.register_next_step_handler(call.message, get_PVR)
        # перезапись фото
        elif call.data == 'rewrite_photo':
            bot.answer_callback_query(callback_query_id=call.id)
            bot.send_message(call.message.chat.id,
                             '❓️ Отправьте ваше фото с семьей во весь рост.\n🚩️ ВНИМАТЕЛЬНО, заявка без фото НЕ принимается.')
            # bot.register_next_step_handler(call.message, all_information)
    except Exception as e:
        bot.send_message(call.message.chat.id, 'Ошибка!')
        print(f'callback_inline_photo exception: {e.args}')


@bot.callback_query_handler(func=lambda call: call.data == 'save_pvr' or call.data == 'rewrite_pvr')
def callback_inline_pvr(call):
    try:
        # сохранение ПВР
        if call.data == 'save_pvr':
            bot.answer_callback_query(callback_query_id=call.id, text="Сохранено!")
            bot.send_message(call.message.chat.id,
                             '❓️ Напишите кто входит в ваш состав семьи.\n (супруг / супруга; родители(отец; мать; дедушка; бабушка);\n дети (сын / дочь / внуки / опекун и т.д.)) \n\n 🚩️ ВНИМАТЕЛЬНО, перечисляйте в одну строку, разделяя запятыми или точкой с запятой.\n Пример: супруг, ребенок, отец, мать')
            bot.register_next_step_handler(call.message, get_family_members)
        # перезапись ПВР
        elif call.data == 'rewrite_pvr':
            bot.answer_callback_query(callback_query_id=call.id)
            bot.send_message(call.message.chat.id,
                             '❓️ Напишите название Вашего ПВР(Звезда, Водник, Лукоморье) и номер комнаты! \n🚩️ Пример: Звезда, 12')
            bot.register_next_step_handler(call.message, get_PVR)
    except Exception as e:
        bot.send_message(call.message.chat.id, 'Ошибка!')
        print(f'callback_inline_telephone exception: {e.args}')

@bot.callback_query_handler(func=lambda call: call.data == 'save_family_members' or call.data == 'rewrite_family_members')
def callback_inline_family(call):
    try:
        chat_id = call.message.chat.id
        user = user_dict[chat_id]
        count_family_stop[chat_id] = len(user.family_members_split)
        count_family[chat_id] = 0
        if call.data == 'save_family_members':
            bot.answer_callback_query(callback_query_id=call.id, text="Сохранено!")
            #проходим по ключам словаря(члены семьи) и получаем каждого члена отдельно(member)
            bot.send_message(call.message.chat.id, f'❓️ {user.family_members_split[count_family[chat_id]]}:\nНапишите ФИО, возраст, рост, размер верхней одежды(размеры РФ: 38, 40 и т.д.), размер нижней одежды(размеры РФ: 38, 40 и т.д.), размер обуви(размеры РФ: 39, 40, 41 и т.д. Для детей в сантиметрах: 24.1, 27.5 и т.д.)\n\n 🚩️ ВНИМАТЕЛЬНО, перечисляйте в одну строку, разделяя запятыми.\n Пример: Иванов Иван Иванович, 42, 180, 50, 50, 27.5')
            bot.register_next_step_handler(call.message, get_every_member_family, user.family_members_split[count_family[chat_id]])
        # переписываем состав семьи(отец, мать, супруг и т.д.)
        elif call.data == 'rewrite_family_members':
            bot.answer_callback_query(callback_query_id=call.id)
            bot.send_message(call.message.chat.id,
                             '❓️ Напишите кто входит в ваш состав семьи.\n (супруг / супруга; родители(отец; мать; дедушка; бабушка);\n дети (сын / дочь / внуки / опекун и т.д.))\n\n 🚩️ ВНИМАТЕЛЬНО, перечисляйте в одну строку, разделяя запятыми или точкой с запятой.\n Пример: супруг, ребенок, отец, мать')
            bot.register_next_step_handler(call.message, get_family_members)
    except Exception as e:
        bot.send_message(call.message.chat.id, 'Ошибка!')
        print(f'callback_inline_family exception: {e.args}')



@bot.callback_query_handler(func=lambda call: call.data == 'save_request' or call.data == 'rewrite_request')
def callback_inline_request(call):
    try:
        if call.data == 'save_request':
            bot.answer_callback_query(callback_query_id=call.id, text="Сохранено!")
            bot.send_message(call.message.chat.id, '🚩️ Проверьте введенную вами информацию.')
            all_information(call.message.chat.id)
        elif call.data == 'rewrite_request':
            bot.answer_callback_query(callback_query_id=call.id)
            bot.send_message(call.message.chat.id,
                             f'❓️  Напишите, что бы вы хотели получить.(одежда, медикаменты, другое)\n\n 🚩️ ВНИМАТЕЛЬНО, отправляйте запрос одним сообщением. Для медикаментов требуется назначение врача.\n Пример: куртка 50р., кроссовки 43р.(28см), футболки 2шт.(48р., 50р.), Лидокаин(назначение 107-1/у)')
            bot.register_next_step_handler(call.message, get_request)
    except Exception as e:
        bot.send_message(call.message.chat.id, 'Ошибка!')
        print(f'callback_inline_request exception: {e.args}')

@bot.callback_query_handler(func=lambda call: call.data == 'save_info' or call.data == 'rewrite_info')
def callback_save_info(call):
    try:
        if call.data == 'save_info':
            bot.answer_callback_query(callback_query_id=call.id, text="Сохранено!")
            bot.send_message(call.message.chat.id, '🚩️ Подождите, заявка записывается')
            save_info_to_GoogleSheet(call.message.chat.id)
            bot.send_message(call.message.chat.id, '🚩️ Заявка записана!  О результатах принятия заявок следите в группе заявок: https://t.me/+pW-Os9lcxgY1NzF')
            #добавление в гугл таблицу и диск

        elif call.data == 'rewrite_info':
            bot.answer_callback_query(callback_query_id=call.id)
            bot.send_message(call.message.chat.id,'Напишите /start и начните сначала')
    except Exception as e:
        bot.send_message(call.message.chat.id, 'Ошибка!')
        print(f'callback_inline_request exception: {e.args}')


@bot.callback_query_handler(func=lambda call: call.data != 'save_family_members' or call.data != 'rewrite_family_members' or call.data != 'save_photo' or call.data != 'rewrite_photo' or call.data != 'save_telephone' or call.data != 'rewrite_telephone' or call.data != 'save_name' or call.data != 'rewrite_name' or call.data != 'save_request' or call.data != 'rewrite_request' or call.data != 'save_info' or call.data != 'rewrite_info')
def callback_inline_members(call):
    try:
        chat_id = call.message.chat.id
        user = user_dict[chat_id]

        #заполняем и сохраняем определенного(count_family) члена семьи
        # когда последний элемент словаря заполнили, запускаем это
        if call.data == f'save_family_members_{user.family_members_split[count_family_stop[chat_id]-1]}':
            bot.answer_callback_query(callback_query_id=call.id, text="Сохранено!")
            bot.send_message(call.message.chat.id,
                                 f'❓️  Напишите, что бы вы хотели получить.(одежда, медикаменты, другое)\n\n 🚩️ ВНИМАТЕЛЬНО, отправляйте запрос одним сообщением. Для медикаментов требуется назначение врача.\n Пример: куртка 50р., кроссовки 43р.(28см), футболки 2шт.(48р., 50р.), Лидокаин(назначение 107-1/у)')
            bot.register_next_step_handler(call.message, get_request)
        # переписываем последний элемент словаря
        elif call.data == f'rewrite_family_members_{user.family_members_split[count_family_stop[chat_id] - 1]}':
            bot.answer_callback_query(callback_query_id=call.id)
            bot.send_message(call.message.chat.id,
                             f'❓️ {user.family_members_split[count_family_stop[chat_id] - 1]}:\nНапишите ФИО, возраст, рост, размер верхней одежды(размеры РФ: 38, 40 и т.д.), размер нижней одежды(размеры РФ: 38, 40 и т.д.), размер обуви(в сантиметрах: 24.1, 27.5 и т.д.)\n\n 🚩️ ВНИМАТЕЛЬНО, перечисляйте в одну строку, разделяя запятыми.\n Пример: Иванов Иван Иванович, 42, 180, 50, 50, 27.5')
            bot.register_next_step_handler(call.message, get_every_member_family, user.family_members_split[count_family_stop[chat_id] - 1])
        elif call.data == f'save_family_members_{user.family_members_split[count_family[chat_id]]}':
            bot.answer_callback_query(callback_query_id=call.id, text="Сохранено!")
            # проходим по ключам словаря(члены семьи) и заполняем каждого члена отдельно
            if count_family_stop[chat_id] == 1:
                bot.send_message(call.message.chat.id,
                                 f'❓️  Напишите, что бы вы хотели получить.(одежда, медикаменты, другое)\n\n 🚩️ ВНИМАТЕЛЬНО, отправляйте запрос одним сообщением. Для медикаментов требуется назначение врача.\n Пример: куртка 50р., кроссовки 43р.(28см), футболки 2шт.(48р., 50р.), Лидокаин(назначение 107-1/у)')
                bot.register_next_step_handler(call.message, get_request)
            else:
                # if count_family[chat_id] == (count_family_stop[chat_id]-1):
                #     count_family[chat_id] == 1
                count_family[chat_id] += 1
                bot.send_message(call.message.chat.id,
                                    f'❓️ {user.family_members_split[count_family[chat_id]]}:\nНапишите ФИО, возраст, рост, размер верхней одежды(размеры РФ: 38, 40 и т.д.), размер нижней одежды(размеры РФ: 38, 40 и т.д.), размер обуви(в сантиметрах: 24.1, 27.5 и т.д.)\n\n 🚩️ ВНИМАТЕЛЬНО, перечисляйте в одну строку, разделяя запятыми.\n Пример: Иванов Иван Иванович, 42, 180, 50, 50, 27.5')
                bot.register_next_step_handler(call.message, get_every_member_family, user.family_members_split[count_family[chat_id]])
        # переписываем определенного(count_family) члена семьи
        elif call.data == f'rewrite_family_members_{user.family_members_split[count_family[chat_id]]}':
            bot.answer_callback_query(callback_query_id=call.id)
            # проходим по ключам словаря(члены семьи) и получаем каждого члена отдельно(member)
            bot.send_message(call.message.chat.id,
                             f'❓️ {user.family_members_split[count_family[chat_id]]}:\nНапишите ФИО, возраст, рост, размер верхней одежды(размеры РФ: 38, 40 и т.д.), размер нижней одежды(размеры РФ: 38, 40 и т.д.), размер обуви(в сантиметрах: 24.1, 27.5 и т.д.)\n\n 🚩️ ВНИМАТЕЛЬНО, перечисляйте в одну строку, разделяя запятыми.\n Пример: Иванов Иван Иванович, 42, 180, 50, 50, 27.5')
            bot.register_next_step_handler(call.message, get_every_member_family, user.family_members_split[count_family[chat_id]])

    except Exception as e:
        bot.send_message(call.message.chat.id, 'Ошибка!')
        print(f'callback_inline_members exception: {e.args}')


#GOOGLE DRIVE AND SHEETS

def autoriz():
    try:
        CREDENTIALS_FILE = 'credentials.json'  # Имя файла с закрытым ключом
        # Читаем ключи из файла
        #Scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'] предоставляют разный уровень доступа к данным
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                       ['https://www.googleapis.com/auth/spreadsheets',
                                                                        'https://www.googleapis.com/auth/drive'])

        httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
        service = googleapiclient.discovery.build('sheets', 'v4',
                                                  http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
        spreadsheetId = '1LB6IahdIufY1HbcqElnTQaTEcRpbSFZwzehsbjtOF2Y'  # сохраняем идентификатор файла
        driveService = googleapiclient.discovery.build('drive', 'v3',
                                                       http=httpAuth)  # Выбираем работу с Google Drive и 3 версию API
        # Доступ к редактированию
        # access = driveService.permissions().create(
        #     fileId=spreadsheetId,
        #     body={'type': 'user', 'role': 'writer', 'emailAddress': 'nikewalce1@gmail.com'},
        #     # Открываем доступ на редактирование
        #     fields='id'
        # ).execute()
        #Гугл-диск, в который сохраняется информация
        #print('https://docs.google.com/spreadsheets/d/' + spreadsheetId)
        return spreadsheetId, service, driveService
    except Exception as e:
        print(f'Autorize exception: {e.args}')


def read_sheet(service, spreadsheetId):
    try:
        # чтение данных ROWS/COLUMNS
        values = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId,
            range='1:1100',
            majorDimension='ROWS'
        ).execute()
        return values
    except Exception as e:
        print(f'read_sheet exception: {e.args}')


def add_to_spreadsheet(line_for_write, number_of_lines_written, spreadsheetId, sheetId, service):
    try:
        # добавление данных
        results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
            "valueInputOption": "USER_ENTERED",
            # Данные воспринимаются, как вводимые пользователем (считается значение формул)
            "data": [
                {"range": f"Заявка!{number_of_lines_written+1}:{number_of_lines_written+1}",
                 "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                 "values": [line_for_write]}
            ]
        }).execute()
    except Exception as e:
        print(f'add_to_spreadsheet exception: {e.args}')

def download_photo_file(file_photo_info, chat_id):
    try:
        downloaded_file = bot.download_file(file_photo_info.file_path)
        src = f'photo_{chat_id}.jpg'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        file_name = f'photo_{chat_id}.jpg'
        return file_name
    except Exception as e:
        print(f'download_photo_file exception: {e.args}')


def delete_local_file(file_name):
    try:
        path = file_name
        os.remove(path)
    except Exception as e:
        print(f'delete_local_file exception: {e.args}')


def files(service, file_name,chat_id):
    try:
        #вывод всех файлов
        #results = service.files().list(fields="nextPageToken, files(id, name, mimeType, createdTime)").execute()
        #найти нужный файл по имени
        #results = service.files().list(fields="nextPageToken, files(id, name, mimeType, parents, createdTime)", q="name contains 'testphoto'").execute()

        #id папки куда загружать
        folder_id = '1kXPK5oDHWxWI5d8-vYv05Z3vGW5OKJaO'

        #название файла, с которым загрузится в папку
        name = file_name
        # путь к файлу
        file_path = f'photo_{chat_id}.jpg'
        #метаданные загружаемого файла
        file_metadata = {
            'name': name,
            'parents': [folder_id]
        }

        #указание по какому пути находится загружаемый файл, а также указание, что мы будем использовать возобновляемую загрузку, что позволит нам загружать большие файлы.
        media = MediaFileUpload(file_path, mimetype='image/jpeg', resumable=True)
        #функцию create, которая позволит загрузить файл на Google Drive.
        r = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        #print(r)
        id_file = r['id']
        link_download_file = f'https://drive.google.com/file/d/{id_file}/view?usp=sharing'
        #print(f'https://drive.google.com/file/d/{id_file}/view?usp=sharing')
        return link_download_file
    except Exception as e:
        print(f'files exception: {e.args}')



def main():
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
