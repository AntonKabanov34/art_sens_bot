#Библиотеки
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3
import os
import re

#Пакеты
from config import DB_NAME, CL_FOLDER_PASS
from datetime import datetime
from queries import QUERIES_USER_INFO, QUERIES_ARTICLE, QUERIES_ADMIN, QUERIES_USER_INFO, QUERIES_COUNT, QUERIES_DOWNLOADS 
from texts import control_list, sales, plot, feedback, ctrl_list, ctrl_list_contest, all_message_text, all_message_text_contest, bot_status, bot_status_contest, confirm_yes, confirm_no, confirm_message_yes, confirm_message_no, confirm_cancle, confirm_message_cancel

class DataBase:
    def __init__(self, db_name):
        """Управляет доступом к БД"""
        self.db_name = db_name
        pass

    def check_db_availability(self) -> bool:
        """Проверяет доступность базы данных"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
            return True
        except sqlite3.Error as e:
            print(f"Ошибка доступа к базе данных: {e}")
            return False
        
    def check_user_id_exists(self, table_name, user_id) -> bool:
        """Проверяет наличие записи в указанной таблице по user_id"""
        if not self.check_db_availability():
            return False
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = QUERIES_USER_INFO["check_user_id_exists"].format(table_name=table_name)
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return result is not None and result[0] == 1
        except sqlite3.Error as e:
            print(f"Ошибка при проверке наличия user_id в таблице {table_name}: {e}")
            return False
    
    def get_id(self, user_id):
        if not self.check_db_availability():
            return None
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = QUERIES_USER_INFO["select_user_id"]
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении id для user_id {user_id}: {e}")
            return None

    def post_user_id(self, user_id) -> bool:
        """Добавляет id пользователя в таблицу user_id"""
        if not self.check_db_availability():
            return False

        if self.check_user_id_exists("user_id", user_id):
            print(f"Пользователь с id {user_id} уже существует в таблице user_id")
            return False

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(QUERIES_USER_INFO["insert_user_id"], (user_id,))
                self.log_success(f"Пользователь с id {user_id} добавлен в таблицу user_id")
                return True
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении user_id: {e}")
            return False

    def post_user_info(self, chat_id, first_name, last_name, username) -> bool:
        """Метод для добавления информации о пользователе в таблицу user_info.
        На вход принимает chat_id, first_name, last_name, username.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Проверяем, существует ли уже запись в таблице user_id
                cursor.execute(QUERIES_USER_INFO["select_user_id"], (chat_id,))
                result = cursor.fetchone()

                if result is None:
                    # Если пользователь не найден, добавляем его в таблицу user_id
                    cursor.execute(QUERIES_USER_INFO["insert_user_id"], (chat_id,))
                    cursor.execute(QUERIES_USER_INFO["select_user_id"], (chat_id,))
                    result = cursor.fetchone()

                user_id_row_id = result[0]

                # Добавляем информацию о пользователе в таблицу user_info
                cursor.execute(QUERIES_USER_INFO["insert_user_info"], (user_id_row_id, first_name, last_name, username))
                self.log_success(f"Информация о пользователе с id {chat_id} добавлена в таблицу user_info")
                return True
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении user_info: {e}")
            return False

    def log_success(self, message):
        """Логирует успешные операции"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} - {message}")

    def exam_admin(self, user_id) -> bool:
        """Проверяет, есть ли админ в списке админов"""
        user_id = self.get_id(user_id)  # Получаем ID из списка всех юзеров

        if not self.check_db_availability():
            return False

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = QUERIES_ADMIN["check_admin_exists"]
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return result is not None and result[0] == 1
        except sqlite3.Error as e:
            print(f"Ошибка при проверке наличия администратора с user_id {user_id}: {e}")
            return False

    def exam_admin_list(self) -> bool:
        """Проверяет на наличие записей в таблице админ"""
        if not self.check_db_availability():
            return False

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = QUERIES_ADMIN["check_admins_table_exists"]
                cursor.execute(query)
                result = cursor.fetchone()
                return result is not None and result[0] == 1
        except sqlite3.Error as e:
            print(f"Ошибка при проверке наличия записей в таблице admins: {e}")
            return False
    
    def add_new_admin(self, user_id):
        """Добавляет в таблицу admin нового пользователя"""
        user_id = self.get_id(user_id)  # Получаем ID из списка всех юзеров

        if not self.check_db_availability():
            return False

        # Проверяем, существует ли уже запись с таким user_id
        if self.exam_admin(user_id):
            print(f"Пользователь с user_id {user_id} уже является администратором")
            return False

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = QUERIES_ADMIN["insert_admin"]
                cursor.execute(query, (user_id,))
                self.log_success(f"Пользователь с user_id {user_id} добавлен в таблицу admin")
                return True
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении нового администратора с user_id {user_id}: {e}")
            return False

    def exam_art(self, art) -> bool:
        """Проверяет, есть ли артикул в базе"""
        if not self.check_db_availability():
            return None #Иначе сломается каскад проверок
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = QUERIES_ARTICLE["check_article_exists"]
                cursor.execute(query, (art,))
                result = cursor.fetchone()[0]
                return result == 1
        except sqlite3.Error as e:
            print(f"Ошибка при проверке наличия артикула {art}: {e}")
            return False

    def exam_file_id(self, art:str) -> bool:
        """"Проверяет наличие file_id в таблице article"""
        if not self.check_db_availability():
            return None #Иначе сломается каскад проверок
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = QUERIES_ARTICLE["check_file_id_exists"]
                cursor.execute(query, (art,))
                result = cursor.fetchone()[0]
                return result == 1
        except sqlite3.Error as e:
            print(f"Ошибка при проверке наличия file_id для артикула {art}: {e}")
            return False

    def get_file_id(self, art: str) -> str:
        """Получает id контрольного личта по артикулу из БД"""
        art = art.lower()
        if not self.check_db_availability():
            return None
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = QUERIES_ARTICLE["select_file_id"]
                cursor.execute(query, (art,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении file_id для артикула {art}: {e}")
            return None
        pass

    def post_new_file_id(self, art:str, file_id:str) -> bool:
        """Находит в таблице article по art file_id и меняет его на новый из входа"""
        art = art.lower()
        if not self.check_db_availability():
            return False
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = QUERIES_ARTICLE["update_file_id"]
                cursor.execute(query, (file_id, art))
                conn.commit()
                self.log_success(f"Обновлен file_id для артикула {art}")
                return True
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении file_id для артикула {art}: {e}")
            return False
        pass

    def get_all_id_users(self, user_id:str) -> str:
        """Обращается к таблице user_id и собирает все user_id доступные в базе, кроме user_id, который метод получил на вход"""
        if not self.check_db_availability():
            return ""

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = QUERIES_USER_INFO["select_all_user_id"]
                cursor.execute(query, (user_id,))
                results = cursor.fetchall()
                user_ids = [result[0] for result in results if result[0] != user_id]
                return user_ids
        except sqlite3.Error as e:
            print(f"Ошибка при получении всех user_id: {e}")
            return ""

    def update_counter(self, table_name, row_name, increment_value):
        """
        Обновляет значение счетчика в таблице.
        На вход принимает имя таблицы, имя строки и значение для прибавления.
        Возвращает True или False в зависимости от успешности операции.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Получаем текущее значение счетчика
                select_query = QUERIES_COUNT["select_counter"].format(table_name=table_name)
                cursor.execute(select_query, (row_name,))
                current_value = cursor.fetchone()

                if current_value is None:
                    print(f"Строка с именем {row_name} не найдена в таблице {table_name}.")
                    return False

                current_value = current_value[0]

                # Вычисляем новое значение счетчика
                new_value = current_value + increment_value

                # Обновляем значение счетчика в таблице
                update_query = QUERIES_COUNT["update_counter"].format(table_name=table_name)
                cursor.execute(update_query, (new_value, row_name))

                # Подтверждение изменений
                conn.commit()
                print(f"Значение счетчика {row_name} в таблице {table_name} обновлено до {new_value}.")
                return True

        except sqlite3.Error as e:
            print(f"Ошибка при обновлении значения счетчика: {e}")
            return False

    def add_download(self, chat_id, article_code):
        """
        Добавляет запись о скачивании артикула пользователем в таблицу downloads.
        На вход принимает chat_id пользователя и артикул.
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Находим user_id по chat_id
                cursor.execute(QUERIES_DOWNLOADS["select_user_id"], (chat_id,))
                user_id_result = cursor.fetchone()

                if user_id_result is None:
                    print(f"Пользователь с chat_id {chat_id} не найден.")
                    return False

                user_id = user_id_result[0]

                # Находим article_id по артикулу
                cursor.execute(QUERIES_DOWNLOADS["select_article_id"], (article_code,))
                article_id_result = cursor.fetchone()

                if article_id_result is None:
                    print(f"Артикул {article_code} не найден.")
                    return False

                article_id = article_id_result[0]

                # Добавляем запись в таблицу downloads
                cursor.execute(QUERIES_DOWNLOADS["insert_download"], (user_id, article_id))

                # Подтверждение изменений
                conn.commit()
                print(f"Запись о скачивании артикула {article_code} пользователем {chat_id} добавлена.")
                return True

        except sqlite3.Error as e:
            print(f"Ошибка при добавлении записи о скачивании: {e}")
            return False

class ControlList(DataBase):
    def __init__(self, db_name, folder_path):
        """Управляет контрольными листами"""
        super().__init__(db_name)
        self.folder_path = folder_path

    def art_clear(self, art:str) -> str:
        """Очищает артикул"""
        return art.strip().lower()

    def all_articles(self) -> list:
        """Возвращает список доступных артикулов"""
        articles = []
        pattern = re.compile(r'^([a-zA-Z0-9]+)_')
        
        for filename in os.listdir(self.folder_path):
            match = pattern.match(filename)
            if match:
                article = match.group(1).lower()
                articles.append(article)
        
        return articles

    def exam_articles(self, articles) -> bool:
        """Проверяет наличие артикла в папке с файлами"""
        all_articles = self.all_articles()

        if articles in all_articles:
            return True
        else:
            return False

    def exam_file(self, art:str) -> str:
        """Возвращает код сценария из каскада проверок:"""
        #make_1 - art/fileid есть в БД
        #make_2 - в БД есть только art
        #make_3 - В БД ничего нет, но файл есть физически
        #make_4 -  файла с такми ART нет физически

        user_art = self.art_clear(art)
        if self.exam_art(user_art):
            if self.exam_file_id(user_art):
                return 'make_1'
            else:
                return 'make_2'
        else:
            if self.exam_articles(user_art):
                return 'make_3'
            else:
                if user_art == 'xxx001':
                    return 'make_2'
                return 'make_4'

    def add_new_articles(self, art: str, file_id: str) -> bool:
        """Добавляет артикул и file_id контрольного листа в таблицу article"""
        if not self.check_db_availability():
            return False
        
        # Очищаем артикул
        art = self.art_clear(art)

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = "INSERT INTO article (art, file_id) VALUES (?, ?)"
                cursor.execute(query, (art, file_id))
                self.log_success(f"Артикул {art} с file_id {file_id} добавлен в таблицу article")
                return True
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении артикула и file_id: {e}")
            return False

    def get_file_path(self, art: str) -> str:
        """Получает путь к файлу по его артикулу"""
        # Очищаем артикул
        art = self.art_clear(art)

        # Создаем словарь с артикулами и путями к файлам
        article_dict = {}
        pattern = re.compile(r'^([a-zA-Z0-9]+)_')
        
        for filename in os.listdir(self.folder_path):
            match = pattern.match(filename)
            if match:
                article = match.group(1).lower()
                file_path = os.path.join(self.folder_path, filename)
                article_dict[article] = file_path

        # Ищем путь к файлу по артикулу
        if art in article_dict:
            return article_dict[art]

        # Если совпадение не найдено, возвращаем None
        return None
    
    def check_art_pattern(self, art: str) -> bool:
        """Проверяет строку на соответствие шаблону XX000 или XXX000"""
        pattern = re.compile(r'^[a-zA-Z]{2,3}\d{3}$')
        return bool(pattern.match(art))

class KeyBoard:
    def __init___(self):
        pass

    def get_main_menu(self):
        """Показывает главное меню"""
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(KeyboardButton(control_list), KeyboardButton(sales))
        markup.row(KeyboardButton(plot), KeyboardButton(feedback))
        return markup
    
    def get_main_menu_2(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(KeyboardButton(control_list))
        markup.row(KeyboardButton(feedback))
        return markup
    
    def get_inline_cl(self):
        """Показываем самую первую и большую кнопку с контрольным листом"""
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(ctrl_list, callback_data=ctrl_list_contest))
        return markup
    
    def get_admin_main_menu(self):
        """Отправляет базовое меню админа"""
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton(all_message_text, callback_data=all_message_text_contest),
            InlineKeyboardButton(bot_status, callback_data=bot_status_contest)
        )
        return keyboard
    
    def get_admin_message_confirm(self):
        """Принтует меню для отправки сообщения всем пользоваителям"""
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton(confirm_yes, callback_data = confirm_message_yes),
            InlineKeyboardButton(confirm_no, callback_data = confirm_message_no)
        )
        keyboard.row(
            InlineKeyboardButton(confirm_cancle, callback_data=confirm_message_cancel)
        )
        return keyboard




db = DataBase(DB_NAME)
cl = ControlList(DB_NAME, CL_FOLDER_PASS)

#print(cl.art_clear('AR2342 '))
#cl.post_file('AR2342 ')
print(cl.all_articles())
#print(cl.exam_articles('ar008'))
#print(cl.get_file_path('ar003'))

print(db.exam_admin_list()) #False
print(db.exam_admin('166476724')) #False
print(db.get_all_id_users('166476724'))

