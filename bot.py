from tabnanny import check
import config
import random
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from states import Estate
from states import Admin
from a1range import A1Range
import keyboards as kb
from data_base import sqlite_db
bot = Bot(config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Глобальные переменные

appart_info = ""
request_id = 1
number_of_rooms = 0
money = 0
area = ""
phone_number = ""
ID = None
disc = ""
greeting = 'Я - <b>твой личный ассистент Grifon</b>, Мы организация, предоставляющая услуги быстрого и качественного подбора недвижимости!'
order_name = ""
order_phone_num = ""
bid_text = ""

# Взаимодействие с таблицей

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SAMPLE_SPREADSHEET_ID = config.TABLE_ID
SAMPLE_RANGE_NAME = 'Лист1'
service = build(
    'sheets', 'v4', credentials=credentials).spreadsheets().values()
result = service.get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                     range=SAMPLE_RANGE_NAME).execute()
data_from_sheet = result.get('values', [])
batch_clear_values_request_body = {
    'ranges': ["Лист1!A2:H1000"],
}

# Подключение базы данных


async def on_startup(_):
    print("Бот вышел в онлайн")
    sqlite_db.sql_start()

# Очистка гугл таблицы перед парсингом


async def clear_gs():
    clear_response = service.batchClear(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        body=batch_clear_values_request_body).execute()

# ////Админская часть////


def check_sub_channel(chat_member):
    print(chat_member['status'])
    if chat_member['status'] != 'left':
        return True
    else:
        return False


@dp.message_handler(commands=['admin'])
async def make_changes_command(message: types.Message):
    if message.chat.type == 'private':
        if check_sub_channel(await bot.get_chat_member(chat_id=config.CHAT_ID, user_id=message.from_user.id)):
            global ID
            ID = message.from_user.id
            admin_name = message.from_user.first_name
            await bot.send_message(message.from_user.id, text="Уважаемый <b>"+str(admin_name)+"</b>, вы перешли в панель администратора", parse_mode='HTML', reply_markup=kb.admin_main_markup)
        else:
            await bot.send_message(message.from_user.id, 'Вам недоступна панель модератора', reply_markup=kb.menu_markup)


@dp.callback_query_handler(text_contains="admin")
async def admin_buttons(call: types.CallbackQuery, state=FSMContext):
    if call.data == "admin_delete":
        await Admin.delete_id.set()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Введите ID заявки, которую нужно удалить:', reply_markup=kb.admin_sub_markup)
    elif call.data == 'admin_exit':
        await state.finish()
        await bot.answer_callback_query(call.id, text="Вы вышли с панели модератора", show_alert=True)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=greeting, parse_mode='html', reply_markup=kb.menu_markup)

# Отмена удаления заявки


@dp.callback_query_handler(text="adminsub_cancel", state="*")
async def cancel_handler(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                text='Панель администратора', reply_markup=kb.admin_main_markup)


# Принятие заявки в группе


@dp.callback_query_handler(text="bid_connect")
async def connect_button(call: types.CallbackQuery):
    bid_msg_id = call.message.message_id
    await sqlite_db.sql_view1_call_command(bid_msg_id)
    await sqlite_db.sql_change_call_command(bid_msg_id, call.from_user.id)
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=config.CHAT_ID, message_id=call.message.message_id, text="🔔 Поступила заявка на звонок \n🔹 ФИО: `"+str(sqlite_db.call_name)+"`\n🔸 Номер: `"+str(sqlite_db.call_phone)+"`\n🔹 Комментарий: \n🔸 Заявку принял(а): `"+str(call.from_user.first_name)+"`", parse_mode='Markdown')
    await bot.send_message(call.from_user.id, "Вы приняли заявку на звонок: \n🔹 ФИО: `"+str(sqlite_db.call_name)+"`\n🔸 Номер: `"+str(sqlite_db.call_phone)+"`\n🔹 Комментарий:", parse_mode='Markdown', reply_markup=kb.admin_bid_markup)
    sqlite_db.call_name = ""
    sqlite_db.call_phone = ""


@dp.callback_query_handler(text_contains="bidmenu")
async def bid_menu_button(call: types.CallbackQuery):
    if call.data == "bidmenu_finish":
        await bot.answer_callback_query(call.id, text="Вы успешно завершили заявку!", show_alert=True)
        await sqlite_db.sql_view2_call_command(call.from_user.id)
        await bot.edit_message_text(chat_id=config.CHAT_ID, message_id=sqlite_db.call_message, text="✅ Заявка выполнена \n🔹 ФИО: `"+str(sqlite_db.call_name)+"`\n🔸 Номер: `"+str(sqlite_db.call_phone)+"`\n🔹 Комментарий: \n🔸 Исполнитель: `"+str(call.from_user.first_name)+"`", parse_mode='Markdown')
        await sqlite_db.sql_delete_call_command(call.from_user.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                    text='Панель администратора', reply_markup=kb.admin_main_markup)
        sqlite_db.call_name = ""
        sqlite_db.call_phone = ""
        sqlite_db.call_message = ""
    # if call.data == "bidmenu_reject":

    # Удаление заявки


@dp.message_handler(state=Admin.delete_id)
async def delete_request(message: types.Message, state: FSMContext):
    if message.chat.type == 'private':
        if message.from_user.id == ID:
            async with state.proxy() as data:
                data['delete_id'] = message.text
            await sqlite_db.sql_delete_command(data['delete_id'], message, state)
            await sqlite_db.sql_parse_command()
            await clear_gs()
            if sqlite_db.del_check == True:
                if sqlite_db.parse != []:
                    array = {'values': sqlite_db.parse}
                    range_ = A1Range.create_a1range_from_list(
                        'Лист1', 2, 1, array['values']).format()
                    response = service.update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                              range=range_,
                                              valueInputOption='RAW', body=array).execute()
                    await bot.send_message(message.from_user.id, "Вы успешно удалили зявку с ID: " + data['delete_id'], reply_markup=kb.admin_main_markup)
                    await state.finish()
                else:
                    await bot.send_message(message.from_user.id, "Вы успешно удалили зявку с ID: " + data['delete_id'], reply_markup=kb.admin_main_markup)
                    await state.finish()
            else:
                if sqlite_db.parse != []:
                    array = {'values': sqlite_db.parse}
                    range_ = A1Range.create_a1range_from_list(
                        'Лист1', 2, 1, array['values']).format()
                    response = service.update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                              range=range_,
                                              valueInputOption='RAW', body=array).execute()
                else:
                    return


# ////Клиентская часть////

# Приветствие и появление главного меню

@dp.message_handler(commands=['start', 'help'], state=None)
async def welcome(message: types.Message):
    if message.chat.type == 'private':
        await bot.send_sticker(message.from_user.id, r'CAACAgIAAxkBAAEEKuxiMHggQNoJKse-Kg4aQkbmTCXEmgACthUAAkwaiUmFljrdCwZhOCME')
        await bot.send_message(message.from_user.id, "Добро пожаловать, " + message.from_user.first_name + " 👋\nЯ - <b>твой личный ассистент Grifon</b>, Мы организация, предоставляющая услуги быстрого и качественного подбора недвижимости!",
                               parse_mode='html', reply_markup=kb.menu_markup)

# Главное меню: реакция на кнопкия


@dp.callback_query_handler(text_contains="menu")
async def menu_buttons(call: types.CallbackQuery, state=FSMContext):
    if call.data == "menu_about":
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Агенство недвижимости Грифон является гарантией качества и надежности для наших клиентов. Постоянная растущая собственная база объектов включает в себя более 400 домов, и более 1000 квартир Одессы, множество коммерческих помещений и эксклюзивных предложений от застройщиков нашего города', reply_markup=kb.about_markup)
    elif call.data == 'menu_estate':
        await bot.answer_callback_query(call.id)
        await Estate.estates.set()
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Что вас интересует?', reply_markup=kb.estate_markup)
    if call.data == 'menu_managers':
        await bot.answer_callback_query(call.id)
        await Admin.order_phone_num.set()
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, 'Тут вы можете оставить свой номер и в течении нескольких минут с вами свяжется менеджер.', reply_markup=kb.contact_markup)

# Главное меню - Менеджеры: реакция на отправленный контакт


@dp.message_handler(content_types=['contact'], state=Admin.order_phone_num)
async def create_call_order(message: types.Message, state=FSMContext):
    if message.chat.type == 'private':
        async with state.proxy() as data:
            data['id'] = random.randint(1000, 9999)
        async with state.proxy() as data:
            data['name'] = message.from_user.first_name
        async with state.proxy() as data:
            data['phone_num'] = message.contact.phone_number
        async with state.proxy() as data:
            data['manager'] = ""
        await bot.send_message(message.from_user.id, "Загрузка...", reply_markup=kb.clear_markup)
        await bot.delete_message(message.from_user.id, message.message_id + 1)
        await bot.send_message(message.from_user.id, "Вы заказали звонок,в скором времени с вами свяжутся ✅", reply_markup=kb.menu_markup)
        msg = await bot.send_message(chat_id=config.CHAT_ID, text="🔔 Поступила заявка на звонок \n🔹 ФИО: `"+str(data['name'])+"`\n🔸 Номер: `"+(data['phone_num'])+"`\n🔹 Комментарий: ", parse_mode='Markdown', reply_markup=kb.admin_chat_markup)
        async with state.proxy() as data:
            data['message_id'] = msg.message_id
        await sqlite_db.sql_add_call_command(state)
        await state.finish()

# Главное меню - Менеджеры: реакция на кнопку назад


@dp.message_handler(state=Admin.order_phone_num)
async def check_call_request(message: types.Message, state=FSMContext):
    if message.chat.type == 'private':
        if message.text == "❌ Отмена":
            await state.finish()
            await bot.send_message(message.from_user.id, greeting, parse_mode='html', reply_markup=kb.menu_markup)

# Главное меню - О нас: реакция на кнопку назад


@dp.callback_query_handler(text="about_back")
async def check_call_request(call: types.CallbackQuery, state=FSMContext):
    await bot.answer_callback_query(call.id)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=greeting, parse_mode='html', reply_markup=kb.menu_markup)


# Главное меню - Подобрать жилье: реакция на кнопки

@dp.callback_query_handler(state=Estate.estates, text_contains="estate")
async def estate_buttons(call: types.CallbackQuery, state=FSMContext):
    if call.data == "estate_buy":
        async with state.proxy() as data:
            data['user_id'] = random.randint(1000, 9999)
        async with state.proxy() as data:
            data['name'] = call.from_user.first_name
        async with state.proxy() as data:
            data['estates'] = "Приобрести недвижимость"
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Сколько комнат вас интересует?', reply_markup=kb.rooms_markup)
    elif call.data == "estate_sell":
        async with state.proxy() as data:
            data['user_id'] = random.randint(1000, 9999)
        async with state.proxy() as data:
            data['name'] = call.from_user.first_name
        async with state.proxy() as data:
            data['estates'] = "Продать недвижимость"
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Сколько комнат в вашей собственности?', reply_markup=kb.rooms_markup)
    if call.data == "estate_rent":
        async with state.proxy() as data:
            data['user_id'] = random.randint(1000, 9999)
        async with state.proxy() as data:
            data['name'] = call.from_user.first_name
        async with state.proxy() as data:
            data['estates'] = "Снять жилье"
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Сколько комнат вас интересует?', reply_markup=kb.rooms_markup)
    elif call.data == "estate_rent_out":
        async with state.proxy() as data:
            data['user_id'] = random.randint(1000, 9999)
        async with state.proxy() as data:
            data['name'] = call.from_user.first_name
        async with state.proxy() as data:
            data['estates'] = "Сдать в аренду жилье"
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Сколько комнат в вашей собственности?', reply_markup=kb.rooms_markup)
    if call.data == 'estate_back':
        await state.finish()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=greeting, parse_mode='html', reply_markup=kb.menu_markup)


# Главное меню - Подобрать жилье - Кол-во комнат: реакция на кнопки
@dp.callback_query_handler(state=Estate.rooms, text_contains="room")
async def estate_buttons(call: types.CallbackQuery, state=FSMContext):
    if call.data == "room_1":
        async with state.proxy() as data:
            data['rooms'] = "1"
        await Estate.next()
        if data['estates'] == "Приобрести недвижимость" or data['estates'] == "Продать недвижимость":
            await bot.answer_callback_query(call.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='На какой бюджет в USD💲 вы расчитываете?', reply_markup=kb.buy_markup)
        elif data['estates'] == "Снять жилье" or data['estates'] == "Сдать в аренду жилье":
            await bot.answer_callback_query(call.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='На какую сумму в USD💲 вы расчитываете?', reply_markup=kb.rent_markup)
    elif call.data == "room_2":
        async with state.proxy() as data:
            data['rooms'] = "2"
        await Estate.next()
        if data['estates'] == "Приобрести недвижимость" or data['estates'] == "Продать недвижимость":
            await bot.answer_callback_query(call.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='На какой бюджет в USD💲 вы расчитываете?', reply_markup=kb.buy_markup)
        elif data['estates'] == "Снять жилье" or data['estates'] == "Сдать в аренду жилье":
            await bot.answer_callback_query(call.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='На какую сумму в USD💲 вы расчитываете?', reply_markup=kb.rent_markup)
    elif call.data == "room_3":
        async with state.proxy() as data:
            data['rooms'] = "3"
        await Estate.next()
        if data['estates'] == "Приобрести недвижимость" or data['estates'] == "Продать недвижимость":
            await bot.answer_callback_query(call.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='На какой бюджет в USD💲 вы расчитываете?', reply_markup=kb.buy_markup)
        elif data['estates'] == "Снять жилье" or data['estates'] == "Сдать в аренду жилье":
            await bot.answer_callback_query(call.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='На какую сумму в USD💲 вы расчитываете?', reply_markup=kb.rent_markup)
    elif call.data == "room_4more":
        async with state.proxy() as data:
            data['rooms'] = "4+"
        await Estate.next()
        if data['estates'] == "Приобрести недвижимость" or data['estates'] == "Продать недвижимость":
            await bot.answer_callback_query(call.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='На какой бюджет в USD💲 вы расчитываете?', reply_markup=kb.buy_markup)
        elif data['estates'] == "Снять жилье" or data['estates'] == "Сдать в аренду жилье":
            await bot.answer_callback_query(call.id)
            await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='На какую сумму в USD💲 вы расчитываете?', reply_markup=kb.rent_markup)
    if call.data == 'room_back':
        await state.reset_state(with_data=False)
        await Estate.estates.set()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Что вас интересует?', reply_markup=kb.estate_markup)

# Главное меню - Подобрать жилье - Кол-во комнат - Цена: реакция на кнопки(покупка)


@dp.callback_query_handler(state=Estate.money, text_contains="pricebuy")
async def second_question_buy(call: types.CallbackQuery, state=FSMContext):
    if call.data == 'pricebuy_one':
        async with state.proxy() as data:
            data['money'] = '25000-45000'
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Какой район вас интересует?', reply_markup=kb.area_markup)
    elif call.data == 'pricebuy_two':
        async with state.proxy() as data:
            data['money'] = '45000-65000'
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Какой район вас интересует?', reply_markup=kb.area_markup)
    elif call.data == 'pricebuy_three':
        async with state.proxy() as data:
            data['money'] = '65000-90000'
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Какой район вас интересует?', reply_markup=kb.area_markup)
    elif call.data == 'pricebuy_four':
        async with state.proxy() as data:
            data['money'] = '90000-130000'
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Какой район вас интересует?', reply_markup=kb.area_markup)
    elif call.data == 'pricebuy_five':
        async with state.proxy() as data:
            data['money'] = '130000-250000'
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Какой район вас интересует?', reply_markup=kb.area_markup)
    elif call.data == 'pricebuy_back':
        await state.reset_state(with_data=False)
        await Estate.rooms.set()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Сколько комнат вас интересует?', reply_markup=kb.rooms_markup)


# Главное меню - Подобрать жилье - Кол-во комнат - Цена: реакция на кнопки(аренда)
@dp.callback_query_handler(state=Estate.money, text_contains="pricerent")
async def second_question_rent(call: types.CallbackQuery, state=FSMContext):
    if call.data == 'pricerent_one':
        async with state.proxy() as data:
            data['money'] = '350-500'
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='В каком районе ваша недвижимость?', reply_markup=kb.area_markup)
    elif call.data == 'pricerent_two':
        async with state.proxy() as data:
            data['money'] = '500-700'
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='В каком районе ваша недвижимость?', reply_markup=kb.area_markup)
    elif call.data == 'pricerent_three':
        async with state.proxy() as data:
            data['money'] = '700-1000'
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='В каком районе ваша недвижимость?', reply_markup=kb.area_markup)
    elif call.data == 'pricerent_four':
        async with state.proxy() as data:
            data['money'] = '1000-1500'
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='В каком районе ваша недвижимость?', reply_markup=kb.area_markup)
    elif call.data == 'pricerent_five':
        async with state.proxy() as data:
            data['money'] = 'Выше 1500'
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='В каком районе ваша недвижимость?', reply_markup=kb.area_markup)
    elif call.data == 'pricerent_back':
        await state.reset_state(with_data=False)
        await Estate.rooms.set()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Сколько комнат в вашей собственности?', reply_markup=kb.rooms_markup)


# Результат третьего вопроса
@dp.callback_query_handler(state=Estate.area, text_contains="area")
async def third_question(call: types.CallbackQuery, state=FSMContext):
    if call.data == 'area_one':
        async with state.proxy() as data:
            data['area'] = "Cуворовский"
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, 'Предоставьте пожалуйста свой номер телефона, менеджер свяжется с вами в ближайшее время', reply_markup=kb.contact_markup)
    elif call.data == 'area_two':
        async with state.proxy() as data:
            data['area'] = "Приморский"
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, 'Предоставьте пожалуйста свой номер телефона, менеджер свяжется с вами в ближайшее время', reply_markup=kb.contact_markup)
    elif call.data == 'area_three':
        async with state.proxy() as data:
            data['area'] = "Киевский"
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, 'Предоставьте пожалуйста свой номер телефона, менеджер свяжется с вами в ближайшее время', reply_markup=kb.contact_markup)
    if call.data == 'area_four':
        async with state.proxy() as data:
            data['area'] = "Малиновский"
        await Estate.next()
        await bot.answer_callback_query(call.id)
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, 'Предоставьте пожалуйста свой номер телефона, менеджер свяжется с вами в ближайшее время', reply_markup=kb.contact_markup)
    if call.data == 'area_back':
        await state.reset_state(with_data=False)
        await Estate.money.set()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='На какой бюджет в USD💲 вы расчитываете?', reply_markup=kb.buy_markup)


# Запрос контакта


@dp.message_handler(state=Estate.phone_num)
async def check_call_request(message: types.Message, state=FSMContext):
    if message.chat.type == 'private':
        if message.text == "❌ Отмена":
            await state.finish()
            await message.reply('Вы отменили действие', reply_markup=kb.menu_markup)

# результат заявки


@dp.message_handler(content_types=['contact'], state=Estate.phone_num)
async def fourth_question(message: types.Message, state=FSMContext):
    if message.chat.type == 'private':
        async with state.proxy() as data:
            data['phone_num'] = message.contact.phone_number
        await Estate.next()
        await bot.send_message(message.from_user.id, "Загрузка...", reply_markup=kb.clear_markup)
        await bot.delete_message(message.from_user.id, message.message_id + 1)
        await bot.send_message(message.from_user.id, "Ваша заявка заполнена: \n\n🏠 Операция: "+str(data['estates'])+"\n🌐 Район: "+str(data['area'])+" \n🔢 Комнаты: "+str(data['rooms'])+"\n💵 Цена (дол.): "+str(data['money'])+"\n📞 Номер телефона: "+str(data['phone_num'])+"\n\nВсё верно?", reply_markup=kb.finish_markup)


@dp.callback_query_handler(state=Estate.finish, text_contains="finish")
async def final_question(call: types.CallbackQuery, state=FSMContext):
    if call.data == "finish_yes":
        await sqlite_db.sql_add_command(state)
        await sqlite_db.sql_parse_command()
        await clear_gs()
        array = {'values': sqlite_db.parse}
        range_ = A1Range.create_a1range_from_list(
            'Лист1', 2, 1, array['values']).format()
        response = service.update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                  range=range_,
                                  valueInputOption='RAW',
                                  body=array).execute()
        await state.finish()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ваша заявка принята и вскоре будет рассмотрена ✅", reply_markup=kb.menu_markup)
    elif call.data == "finish_no":
        await state.reset_state(with_data=False)
        await Estate.estates.set()
        await bot.answer_callback_query(call.id)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Отредактируйте вашу заявку", reply_markup=kb.estate_markup)


# ***********************************Запуск бота***********************************

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
