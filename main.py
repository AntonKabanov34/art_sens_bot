#Библиотеки
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputFile

import asyncio

#Пакеты
from texts import hi, welcome, ctrl_list_contest, post_art, control_list, sales, plot, feedback, all_message_text_contest, bot_status_contest, post_all_message, post_message_check, post_message_check_confirm, confirm_message_yes, confirm_message_no, confirm_message_cancel, post_message_reply, post_message_cancel
from clases import DataBase, ControlList, KeyBoard
from config import BOT_TOKEN, DB_NAME, CL_FOLDER_PASS


#config
API_TOKEN = BOT_TOKEN
db = DataBase(DB_NAME)
cl = ControlList(DB_NAME, CL_FOLDER_PASS)
keyboard = KeyBoard()

GIF = 'BAACAgIAAxkBAAMHZzcrtbtEL5l4owLYZ2HhRiedun8AAipcAAJuEJFIkiBFiKGf9V02BA'

# Настройка логирования
#logging.basicConfig(level=logging.INFO)

# Настройка хранилища состояний
storage = MemoryStorage()

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


#Проверка доступности файла
async def chek_file(file_id) -> bool:
    """Проверяет доступность файла на сервере ТГ по file_id"""
    try:
        file_info = await bot.get_file(file_id)
        return True
    except Exception as e:
        logging.error(f"Ошибка при проверке доступности файла с file_id {file_id}: {e}")
        return False

async def get_file_id(chat_id, file_path) -> str:
    """Отправляет в ТГ файл получает file_id и возвращает его, на вход принимает путь к файлу"""
    try:
        # Отправляем файл в Telegram и получаем объект Message
        with open(file_path, 'rb') as file:
            message = await bot.send_document(chat_id=chat_id, document=InputFile(file), reply_markup=keyboard.get_main_menu_2())
        # Извлекаем file_id из отправленного документа
        file_id = message.document.file_id
        return file_id
    except Exception as e:
        logging.error(f"Ошибка при отправке файла и получении file_id: {e}")
        return None
    
# Определение состояний FSM
class UserStates(StatesGroup):
    wait_for_art = State()

class AdminMessage(StatesGroup):
    write_message = State()
    confirm_message = State()


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    db.post_user_id(message.from_user.id)
    db.post_user_info(message.from_user.id, message.from_user.first_name,
                      message.from_user.last_name, message.from_user.username)
    #Прикрутить сюда сперва инлайн, а затем
    await bot.send_message(message.from_user.id, text= hi + message.from_user.first_name + "!", reply_markup=keyboard.get_main_menu_2())
    await bot.send_message(message.from_user.id, welcome, reply_markup=keyboard.get_inline_cl())



#_________Обработкчик кнопок из MainMenu___________

#Обработчик команды getControlList
@dp.message_handler(lambda message: message. text in [control_list, sales, plot, feedback])
async def get_control_list_menu(message: types.Message):
    
    #Контрольный лист
    if message.text == control_list:
        db.update_counter('counters', 'tap_serch', 1)
        await bot.send_animation(
            chat_id=message.from_user.id,
            animation=GIF,
            caption='Артикул можно найти в коробке (как в анимации), а также на самой картине! Обычно он выглядит как XXX001, где XXX - это латинские буквы.')
        await bot.send_message(message.from_user.id, 'Введите артикул:')
        await UserStates.wait_for_art.set()
    #Скидки
    elif message.text == sales:
        await bot.send_message(message.from_user.id, text='Пока здесь тихо...но....\nСкоро здесь будет информация о наших акциях и скидках!')
        pass
   # Топ сюжеты 
    elif message.text ==plot:
        await bot.send_message(message.from_user.id, text='Хмммм, у нас очень много сюжетов! Сейчас мы думаем, как бы вам предложить тот сюжет, который понравится на 1000%.\nА пока, почаще заходите на наши маркетплейсы и выбирайте самые лучшие товары для хобби и творчества!')
        pass
    # Обратная связь
    elif message.text == feedback:
        await bot.send_message(message.from_user.id, text='Мы всегда на связи и оперативно отвечаем в течении 48 часов.\nЕсли у вас возникли проблемы, вопросы или предложения по нашим продуктам, направляйте их на почту example@example.ru')
        db.update_counter('counters', 'tap_support', 1)
        pass

# Обработчик колбеков
@dp.callback_query_handler(lambda c: c.data in [ctrl_list_contest, all_message_text_contest, bot_status_contest])
async def process_callback_control_list(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    if callback_query.data == ctrl_list_contest:
        db.update_counter('counters', 'tap_serch', 1)
        await bot.send_animation(
        chat_id=callback_query.from_user.id,
        animation=GIF,
        caption='Артикул можно найти в коробке (как в анимации), а также на самой картине! Обычно он выглядит как XXX001, где XXX - это латинские буквы.')
        await bot.send_message(callback_query.from_user.id, post_art)
        await UserStates.wait_for_art.set()

    #Отправка сообщений всем пользователям
    elif callback_query.data == all_message_text_contest:
        await AdminMessage.write_message.set()
        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text = post_all_message)
        pass

    #Сообщение о статусе БОТА
    elif callback_query.data == bot_status_contest:
        pass

# Состояние FSM - Обработка контрольных листов    
@dp.message_handler(state=UserStates.wait_for_art)
async def process_text(message: types.Message, state: FSMContext):
    user_text = message.text
    file_path = cl.get_file_path(user_text)

    if cl.exam_file(user_text) == 'make_1':
        print(f'{user_text} в базе данных есть, существует также и файл айди')
        file_id = db.get_file_id(user_text)
        
        if await chek_file(file_id):
            await bot.send_document(chat_id=message.chat.id, document=file_id)
            db.add_download(message.chat.id, user_text.lower())
        else:
            await bot.send_chat_action(chat_id=message.chat.id, action=types.ChatActions.UPLOAD_DOCUMENT)
            db.post_new_file_id(user_text, await get_file_id(message.from_user.id, file_path))
            db.add_download(message.chat.id, user_text.lower())
            await asyncio.sleep(1)
            pass
    
    elif cl.exam_file(user_text) == 'make_2':
        print(f'АЛАРМ! АБСОЛЮТНО НЕРЕАЛЬНАЯ СИТУАЦИЯ! {user_text} в базе данных есть, ФАЙЛ АЙДИ В БАЗЕ НЕТ')
        await bot.send_message(message.from_user.id, text='Ахахахахха!\nМы в вас не сомневались, вы взломали систему!\nДержите промокод: ПРОМОКОД')
        pass
    
    #Отправляем файл, добавляем артикул и файл айди в базу
    elif cl.exam_file(user_text) == 'make_3':
        print(f'{user_text} в базе данных НЕТ, ФАЙЛ АЙДИ В БАЗЕ НЕТ - НО САМ ФАЙЛ ЕСТЬ')
        await bot.send_chat_action(chat_id=message.chat.id, action=types.ChatActions.UPLOAD_DOCUMENT)
        cl.add_new_articles(user_text, await get_file_id(message.from_user.id, file_path))
        db.add_download(message.chat.id, user_text.lower())
        await asyncio.sleep(1)
        
    elif cl.exam_file(user_text) == 'make_4':
        print(f'{user_text} в базе данных НЕТ, ФАЙЛ АЙДИ НЕТ - ФИЗИЧЕСКИ НЕТ ТАКОГО ФАЙЛА')
        await message.answer(f'Mы не нашли контрольный лист для картины с артикулом "{user_text}". Пожалуйста, проверьте правильность написания артикула и повторите попытку еще раз через меню бота.',reply_markup=keyboard.get_main_menu_2())
        pass
    else:
        print(f'Непредвиденный сценарий с артикулом {user_text}')

    await state.finish()  # Завершаем состояние

# Состояние FSM для ОТПРАВКИ СООБЩЕНИЙ ВСЕМ ПОЛЬЗОВАТЕЛЯМ
@dp.message_handler(state=AdminMessage.write_message)
async def write_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['message_text'] = message.text
    await AdminMessage.next()
    await bot.send_message(message.from_user.id, f'{post_message_check}\n\n"{message.text}"\n\n{post_message_check_confirm}', reply_markup=keyboard.get_admin_message_confirm())

@dp.callback_query_handler(lambda c: c.data in [confirm_message_yes, confirm_message_no, confirm_message_cancel], state=AdminMessage.confirm_message)
async def post_confirm_message(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    #Отправляем сообщение
    if callback_query.data == confirm_message_yes:
        # Сделать метод получения всех ID
        async with state.proxy() as data:
            message_text = data['message_text']
            users = db.get_all_id_users(callback_query.from_user.id)
            eror_users = 0
            mess_admin = f'Сообщение отправлено: {len(users)} пользователям.\nПри отправлении возникло: {eror_users} ошибок. Сообщения не доставлены: пользователь не найден или он заблокировал бота.'
            for user_id in users:
                if user_id == callback_query.from_user.id:
                    continue
                try:
                    await bot.send_message(chat_id=user_id, text=message_text)
                except Exception as e:
                    eror_users = eror_users + 1
            await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id, text=mess_admin)
            await state.finish()
    
    # Перезапускаем ФСМ
    elif callback_query.data == confirm_message_no:
        await bot.edit_message_text(chat_id = callback_query.from_user.id, message_id = callback_query.message.message_id, text=post_message_reply)
        await AdminMessage.write_message.set()

    # Выходим из состояния
    elif callback_query.data == confirm_message_cancel:
        await bot.edit_message_text(chat_id = callback_query.from_user.id, message_id = callback_query.message.message_id, text=post_message_cancel)
        await state.finish()


#Подсказки для пользователя
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_text_messages(message: types.Message):
    user_text = message.text.lower()
    if cl.check_art_pattern(user_text):
        await bot.send_message(message.from_user.id, f'Кажется, вы пытаетесь получить контрольный лист по артикулу {user_text}.\nЕсли это так, то нажмите на кнопку ниже и введите артикул⤵️', reply_markup=keyboard.get_inline_cl())
        pass
    elif user_text == 'get_god_menu':
        #Проверяем таблицу на 0 
        if db.exam_admin_list():
            # Проверяем на наличие ID в этой таблице
            if db.exam_admin(message.from_user.id):
                #Принтуем клавиатуру Админа
                await bot.send_message(message.from_user.id, 'Приветствую тебя создатель!', reply_markup=keyboard.get_admin_main_menu())
                pass
            else:
                print('Человек который обратился к меню андмина, не является админом')
                pass
        else:
            #Добавляем первого админа и принтуем ему клавиатуру админа
            db.add_new_admin(message.from_user.id)
            await bot.send_message(message.from_user.id, 'Приветствую тебя создатель!', reply_markup=keyboard.get_admin_main_menu())
            pass
    else:
        #если сообщение не похоже на артикул, просто ничего не делаем
        pass


if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
